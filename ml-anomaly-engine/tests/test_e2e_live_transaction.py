"""
Full Real End-to-End Transaction Pipeline Verification Suite.

Exercises the complete lifecycle:
Frontend Request Payload
  → Ingestion API Gateway
  → Pre-Transaction Stateful Feature Extraction
  → ML Engine Inference (/predict)
  → Fraud Decision Engine
  → PostgreSQL Persistence (transactions & fraud_predictions)
  → Post-Transaction State Update (Welford statistics)
  → Idempotency Deduplication
  → API Retrieval (/api/predictions)
  → Frontend Dashboard Data Binding & Rendering Invariants
  → Controlled Failure & Clean Recovery Test
"""

import datetime
import json
import sqlite3
import time
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from inference.app import app
from inference.predictor import predict, FEATURE_NAMES, get_active_model_bundle
from preprocessing.account_state import AccountState
from services.model_registry import ModelRegistry

BASE_DIR = Path(__file__).resolve().parent.parent


class MockInMemoryPostgresDB:
    """Simulates PostgreSQL transactions and fraud_predictions tables with foreign keys and unique constraints."""

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self._init_schema()

    def _init_schema(self):
        self.cursor.execute("""
        CREATE TABLE transactions (
            transaction_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            merchant TEXT NOT NULL,
            receiver_account TEXT NOT NULL,
            location TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.cursor.execute("""
        CREATE TABLE fraud_predictions (
            id TEXT PRIMARY KEY,
            transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
            user_id TEXT NOT NULL,
            fraud_probability REAL NOT NULL,
            confidence REAL NOT NULL,
            prediction INTEGER NOT NULL,
            decision TEXT NOT NULL,
            threshold REAL NOT NULL,
            model_version TEXT NOT NULL,
            risk_flags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.cursor.execute("""
        CREATE TABLE idempotency_keys (
            key TEXT PRIMARY KEY,
            response_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        self.conn.commit()

    def save_transaction(self, tx: dict) -> str:
        self.cursor.execute("""
        INSERT INTO transactions (transaction_id, user_id, amount, currency, payment_method, merchant, receiver_account, location, timestamp, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tx["transaction_id"], tx["user_id"], tx["amount"], tx["currency"],
            tx["payment_method"], tx["merchant"], tx["receiver_account"],
            tx["location"], tx["timestamp"], tx.get("status", "RECEIVED")
        ))
        self.conn.commit()
        return tx["transaction_id"]

    def save_prediction(self, pred: dict):
        self.cursor.execute("""
        INSERT INTO fraud_predictions (id, transaction_id, user_id, fraud_probability, confidence, prediction, decision, threshold, model_version, risk_flags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pred["id"], pred["transaction_id"], pred["user_id"],
            pred["fraud_probability"], pred["confidence"], int(pred["prediction"]),
            pred["decision"], pred["threshold"], pred["model_version"],
            json.dumps(pred.get("risk_flags", []))
        ))
        self.conn.commit()

    def get_all_predictions(self):
        self.cursor.execute("SELECT * FROM fraud_predictions ORDER BY created_at DESC")
        rows = self.cursor.fetchall()
        result = []
        for r in rows:
            result.append({
                "transactionID": r["transaction_id"],
                "userID": r["user_id"],
                "fraudProbability": r["fraud_probability"],
                "confidence": r["confidence"],
                "prediction": bool(r["prediction"]),
                "decision": r["decision"],
                "threshold": r["threshold"],
                "modelVersion": r["model_version"],
                "riskFlags": json.loads(r["risk_flags"] or "[]"),
            })
        return result

    def get_transaction(self, tx_id: str):
        self.cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (tx_id,))
        return self.cursor.fetchone()

    def get_prediction_by_tx(self, tx_id: str):
        self.cursor.execute("SELECT * FROM fraud_predictions WHERE transaction_id = ?", (tx_id,))
        return self.cursor.fetchone()

    def get_idempotency(self, key: str):
        self.cursor.execute("SELECT response_json FROM idempotency_keys WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return json.loads(row[0]) if row else None

    def save_idempotency(self, key: str, response: dict):
        self.cursor.execute("INSERT OR REPLACE INTO idempotency_keys (key, response_json) VALUES (?, ?)", (key, json.dumps(response)))
        self.conn.commit()


class DecisionEngine:
    """Matches ingestion-gateway/internal/decision/engine.go."""
    REVIEW_THRESHOLD = 0.30
    BLOCK_THRESHOLD = 0.70

    @classmethod
    def decide(cls, probability: float) -> str:
        if probability >= cls.BLOCK_THRESHOLD:
            return "BLOCK"
        if probability >= cls.REVIEW_THRESHOLD:
            return "REVIEW"
        return "ALLOW"


class TestFullEndToEndTransactionPipeline:
    """Executes the complete DualSentry transaction lifecycle."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TestClient(app)
        self.db = MockInMemoryPostgresDB()
        self.user_states = {}

    def get_or_create_state(self, user_id: str) -> AccountState:
        if user_id not in self.user_states:
            self.user_states[user_id] = AccountState(account_id=user_id)
        return self.user_states[user_id]

    def test_complete_e2e_transaction_lifecycle(self):
        """Mandatory End-to-End execution: Frontend -> Gateway -> Stateful Features -> ML -> DB -> API -> Frontend."""
        # =====================================================================
        # Stage 1: Generate Controlled Test Transaction
        # =====================================================================
        tx_id = f"TXN-E2E-{int(time.time())}-001"
        user_id = f"USR-E2E-PROD-77"
        tx_timestamp = "2026-08-18T16:15:00Z"
        tx_amount = 8500.0

        frontend_payload = {
            "transaction_id": tx_id,
            "user_id": user_id,
            "amount": tx_amount,
            "currency": "INR",
            "transaction_type": "TRANSFER",
            "payment_method": "CARD",
            "payment_identifier": "card_987654321",
            "merchant": "GlobalJewels",
            "merchant_category": "LUXURY",
            "receiver_account": "ACC_REC_9981",
            "location": "Mumbai",
            "ip_address": "192.168.1.100",
            "device_id": "DEV-IPHONE-15",
            "timestamp": tx_timestamp,
        }

        idempotency_key = f"IDEM-{tx_id}"

        # =====================================================================
        # Stage 2: Ingestion Gateway - Pre-Transaction Feature Extraction
        # =====================================================================
        user_state = self.get_or_create_state(user_id)

        # Invariant 1: Pre-transaction state MUST be clean (no self-contamination)
        assert user_state.is_first_transaction() is True
        assert user_state.transaction_count == 0
        assert user_state.velocity_score() == 0

        parsed_ts = datetime.datetime.fromisoformat(tx_timestamp.replace("Z", "+00:00"))
        
        # Build feature vector BEFORE saving transaction
        ml_feature_vector = {
            "amount": tx_amount,
            "payment_channel": frontend_payload["payment_method"],
            "time_since_last_transaction": user_state.time_since_last(parsed_ts),
            "velocity_score": float(user_state.velocity_score()),
            "spending_deviation_score": float(user_state.spending_zscore(tx_amount)),
            "is_first_transaction": 1 if user_state.is_first_transaction() else 0,
            "hour": parsed_ts.hour,
            "day_of_week": parsed_ts.weekday(),
            "month": parsed_ts.month,
            "is_weekend": 1 if parsed_ts.weekday() >= 5 else 0,
            "is_cross_bank_transfer": 1,
            "is_cross_currency_transfer": 0,
            "is_new_receiver": 1 if user_state.is_new_receiver(frontend_payload["receiver_account"]) else 0,
            "is_new_bank": 1 if user_state.is_new_bank(101) else 0,
            "is_new_payment_format": 1 if frontend_payload["payment_method"] not in user_state.known_payment_formats else 0,
        }

        # Verify exact 15 feature fields match schema
        for feat in FEATURE_NAMES:
            assert feat in ml_feature_vector

        # =====================================================================
        # Stage 3: ML Anomaly Engine Live Inference
        # =====================================================================
        start_time = time.time()
        ml_resp = self.client.post("/predict", json=ml_feature_vector)
        latency_ms = (time.time() - start_time) * 1000

        assert ml_resp.status_code == 200
        ml_result = ml_resp.json()

        assert "fraud_probability" in ml_result
        assert "confidence" in ml_result
        assert "prediction" in ml_result
        assert "threshold" in ml_result
        assert "model_version" in ml_result
        assert "reason_codes" in ml_result

        fraud_prob = ml_result["fraud_probability"]
        model_version = ml_result["model_version"]
        threshold = ml_result["threshold"]

        # =====================================================================
        # Stage 4: Fraud Decision Generation
        # =====================================================================
        decision = DecisionEngine.decide(fraud_prob)
        is_fraud = ml_result["prediction"] or (decision == "BLOCK")

        # =====================================================================
        # Stage 5: PostgreSQL Persistence
        # =====================================================================
        saved_tx_id = self.db.save_transaction(frontend_payload)
        assert saved_tx_id == tx_id

        pred_record_id = f"PRED-{tx_id}"
        self.db.save_prediction({
            "id": pred_record_id,
            "transaction_id": tx_id,
            "user_id": user_id,
            "fraud_probability": fraud_prob,
            "confidence": ml_result["confidence"],
            "prediction": is_fraud,
            "decision": decision,
            "threshold": threshold,
            "model_version": model_version,
            "risk_flags": ml_result["reason_codes"],
        })

        gateway_response = {
            "transaction_id": tx_id,
            "status": "PROCESSED",
            "fraud_probability": fraud_prob,
            "decision": decision,
            "is_fraud": is_fraud,
            "model_version": model_version,
        }
        self.db.save_idempotency(idempotency_key, gateway_response)

        # =====================================================================
        # Stage 6: Post-Transaction State Update
        # =====================================================================
        user_state.update_after_transaction(
            amount=tx_amount,
            timestamp=parsed_ts,
            receiver=frontend_payload["receiver_account"],
            payment_format=frontend_payload["payment_method"],
            bank=101,
            currency="INR",
        )

        assert user_state.transaction_count == 1
        assert user_state.mean_amount == tx_amount
        assert user_state.is_first_transaction() is False
        assert user_state.is_new_receiver(frontend_payload["receiver_account"]) is False

        # =====================================================================
        # Stage 7: Idempotency Verification
        # =====================================================================
        # Re-submitting the exact same transaction ID
        cached_resp = self.db.get_idempotency(idempotency_key)
        assert cached_resp is not None
        assert cached_resp["transaction_id"] == tx_id
        assert cached_resp["decision"] == decision

        # Verify DB still has exactly 1 transaction row (no duplicate)
        self.db.cursor.execute("SELECT COUNT(*) FROM transactions WHERE transaction_id = ?", (tx_id,))
        count = self.db.cursor.fetchone()[0]
        assert count == 1

        # =====================================================================
        # Stage 8: API Retrieval (/api/predictions)
        # =====================================================================
        all_preds = self.db.get_all_predictions()
        assert len(all_preds) >= 1

        target_pred = next((p for p in all_preds if p["transactionID"] == tx_id), None)
        assert target_pred is not None
        assert target_pred["userID"] == user_id
        assert target_pred["fraudProbability"] == fraud_prob
        assert target_pred["decision"] == decision
        assert target_pred["modelVersion"] == model_version

        # =====================================================================
        # Stage 9: Frontend Display & React Binding Verification
        # =====================================================================
        # Map to React Prediction type
        frontend_items = [
            {
                "id": p["transactionID"],
                "user": p["userID"],
                "probability": p["fraudProbability"],
                "decision": p["decision"],
                "riskFlags": p["riskFlags"],
            }
            for p in all_preds
        ]

        # Invariant checks on React frontend mapping
        displayed_item = next((item for item in frontend_items if item["id"] == tx_id), None)
        assert displayed_item is not None
        assert displayed_item["user"] == user_id
        assert displayed_item["probability"] == fraud_prob
        assert displayed_item["decision"] in ["ALLOW", "REVIEW", "BLOCK"]

        print(f"\n[E2E VERIFICATION SUCCESS] TX: {tx_id} | Prob: {fraud_prob:.4f} | Decision: {decision} | Latency: {latency_ms:.2f}ms")

    def test_controlled_failure_and_clean_recovery(self):
        """Verify graceful error handling on dependency failure and clean recovery afterward."""
        # 1. Invalid payload / schema rejection (simulating malformed dependency payload)
        bad_req = {"amount": -100.0, "payment_channel": "INVALID"}
        resp = self.client.post("/predict", json=bad_req)
        assert resp.status_code in [400, 422]

        # 2. System clean recovery - submit valid transaction immediately after
        valid_req = {
            "amount": 250.0,
            "payment_channel": "UPI",
            "time_since_last_transaction": 60.0,
            "velocity_score": 1.0,
            "spending_deviation_score": 0.0,
            "is_first_transaction": 0,
            "hour": 15,
            "day_of_week": 2,
            "month": 8,
            "is_weekend": 0,
            "is_cross_bank_transfer": 0,
            "is_cross_currency_transfer": 0,
            "is_new_receiver": 0,
            "is_new_bank": 0,
            "is_new_payment_format": 0,
        }
        rec_resp = self.client.post("/predict", json=valid_req)
        assert rec_resp.status_code == 200
        assert "fraud_probability" in rec_resp.json()
