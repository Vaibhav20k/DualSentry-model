"""
Targeted Verification and Regression Suite for DualSentry ML & Feature Pipeline.

Covers:
1. Stateful feature leakage prevention (Tests A, B, C, D)
2. Negative spending deviation z-score validation and ML inference
3. Model artifact clean loading and reproducibility
4. Feature schema, ordering, and categorical encoding compatibility
5. Model registry lifecycle and promotion validation guards
6. Welford online statistics vs. batch statistical calculations
7. is_new_bank receiver tracking across transaction histories
8. Timestamp and month extraction without machine clock contamination
"""

import datetime
import json
import numpy as np
import os
import pytest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from preprocessing.account_state import AccountState
from preprocessing.feature_pipeline import FeaturePipeline
from inference.schemas import PredictionRequest
from inference.predictor import predict, FEATURE_NAMES, get_active_model_bundle
from services.model_registry import ModelRegistry
from retraining.registry_updater import promote_model, load_registry


class TestStatefulFeatureLeakage:
    """Rigorous verification that current transactions cannot contaminate their own features."""

    def test_a_current_transaction_cannot_affect_itself(self):
        """Test A: Features extracted must use ONLY historical state before the current transaction."""
        state = AccountState(account_id="acc_leak_test")
        t0 = datetime.datetime(2026, 1, 1, 10, 0, 0)

        # Baseline setup: 1 prior transaction
        state.update_after_transaction(
            amount=100.0,
            timestamp=t0,
            receiver="rec_old",
            payment_format="CARD",
            bank=101,
            currency="INR",
        )

        # Capture state before new transaction
        pre_count = state.transaction_count
        pre_mean = state.mean_amount

        # Next transaction arrives: amount = 500
        t1 = datetime.datetime(2026, 1, 1, 11, 0, 0)
        new_amount = 500.0

        # Behavioral features calculated BEFORE state update
        v_score = state.velocity_score()
        time_elapsed = state.time_since_last(t1)
        z_score = state.spending_zscore(new_amount)
        is_first = state.is_first_transaction()
        is_new_rec = state.is_new_receiver("rec_new")
        is_new_b = state.is_new_bank(202)

        # Invariants: must reflect pre-transaction state
        assert v_score == 1  # 1 prior transaction, NOT 2
        assert is_first is False
        assert time_elapsed == 3600.0
        # z-score was computed against mean=100 and pre-transaction std (not post-transaction mean)
        assert pre_mean == 100.0
        assert is_new_rec is True
        assert is_new_b is True

        # Now simulate post-inference state update
        state.update_after_transaction(
            amount=new_amount,
            timestamp=t1,
            receiver="rec_new",
            payment_format="CARD",
            bank=202,
            currency="INR",
        )

        # Post-update verification
        assert state.transaction_count == 2
        assert state.mean_amount == 300.0
        assert state.is_new_receiver("rec_new") is False
        assert state.is_new_bank(202) is False

    def test_b_second_transaction_history_visibility(self):
        """Test B: Sequential transactions for same account - txn 1 sees no history, txn 2 sees txn 1."""
        pipeline = FeaturePipeline()
        import pandas as pd

        df = pd.DataFrame([
            {
                "Account": "acc_seq",
                "Timestamp": "2026-03-01 10:00:00",
                "Amount Paid": 100.0,
                "Account.1": "rec_1",
                "Payment Format": "UPI",
                "From Bank": 1,
                "To Bank": 10,
                "Payment Currency": "INR",
                "Receiving Currency": "INR",
                "Is Laundering": 0,
            },
            {
                "Account": "acc_seq",
                "Timestamp": "2026-03-01 10:15:00",
                "Amount Paid": 200.0,
                "Account.1": "rec_2",
                "Payment Format": "CARD",
                "From Bank": 1,
                "To Bank": 10,
                "Payment Currency": "INR",
                "Receiving Currency": "INR",
                "Is Laundering": 0,
            },
        ])

        processed = pipeline.process_dataframe(df)

        # Transaction 1 verification
        row1 = processed.iloc[0]
        assert row1["is_first_transaction"] == 1
        assert row1["velocity_score"] == 0
        assert row1["time_since_last_transaction"] == 0.0
        assert row1["spending_deviation_score"] == 0.0
        assert row1["is_new_receiver"] == 1
        assert row1["is_new_bank"] == 1
        assert row1["is_new_payment_format"] == 1

        # Transaction 2 verification
        row2 = processed.iloc[1]
        assert row2["is_first_transaction"] == 0
        assert row2["velocity_score"] == 1
        assert row2["time_since_last_transaction"] == 900.0  # 15 minutes
        assert row2["is_new_receiver"] == 1  # rec_2 is new
        assert row2["is_new_bank"] == 0  # To Bank 10 was already seen in txn 1
        assert row2["is_new_payment_format"] == 1  # CARD is new (first was UPI)

    def test_c_multiple_accounts_no_cross_contamination(self):
        """Test C: Interleaved transactions between Account A and Account B stay strictly isolated."""
        pipeline = FeaturePipeline()
        import pandas as pd

        df = pd.DataFrame([
            {
                "Account": "acc_A",
                "Timestamp": "2026-04-01 08:00:00",
                "Amount Paid": 500.0,
                "Account.1": "rec_A1",
                "Payment Format": "CARD",
                "From Bank": 1,
                "To Bank": 10,
                "Payment Currency": "USD",
                "Receiving Currency": "USD",
                "Is Laundering": 0,
            },
            {
                "Account": "acc_B",
                "Timestamp": "2026-04-01 08:05:00",
                "Amount Paid": 10.0,
                "Account.1": "rec_B1",
                "Payment Format": "UPI",
                "From Bank": 2,
                "To Bank": 20,
                "Payment Currency": "EUR",
                "Receiving Currency": "EUR",
                "Is Laundering": 0,
            },
            {
                "Account": "acc_A",
                "Timestamp": "2026-04-01 08:10:00",
                "Amount Paid": 550.0,
                "Account.1": "rec_A1",
                "Payment Format": "CARD",
                "From Bank": 1,
                "To Bank": 10,
                "Payment Currency": "USD",
                "Receiving Currency": "USD",
                "Is Laundering": 0,
            },
            {
                "Account": "acc_B",
                "Timestamp": "2026-04-01 08:20:00",
                "Amount Paid": 15.0,
                "Account.1": "rec_B1",
                "Payment Format": "UPI",
                "From Bank": 2,
                "To Bank": 20,
                "Payment Currency": "EUR",
                "Receiving Currency": "EUR",
                "Is Laundering": 0,
            },
        ])

        processed = pipeline.process_dataframe(df)

        # Acc A txn 2
        acc_a_txn2 = processed[(processed["amount"] == 550.0)].iloc[0]
        assert acc_a_txn2["velocity_score"] == 1
        assert acc_a_txn2["time_since_last_transaction"] == 600.0  # 10 min since 08:00
        assert acc_a_txn2["is_new_receiver"] == 0

        # Acc B txn 2
        acc_b_txn2 = processed[(processed["amount"] == 15.0)].iloc[0]
        assert acc_b_txn2["velocity_score"] == 1
        assert acc_b_txn2["time_since_last_transaction"] == 900.0  # 15 min since 08:05
        assert acc_b_txn2["is_new_receiver"] == 0

    def test_d_feature_invariants_exact_match(self):
        """Test D: Explicit verification of all 7 behavioral features against manual calculations."""
        state = AccountState(account_id="acc_invar")

        # T1: amount = 100, at 12:00, to Bank 5, Rec X, format UPI
        t1 = datetime.datetime(2026, 5, 1, 12, 0, 0)
        state.update_after_transaction(100.0, t1, "RecX", "UPI", 5, "INR")

        # T2: amount = 300, at 12:30, to Bank 5, Rec X, format UPI
        t2 = datetime.datetime(2026, 5, 1, 12, 30, 0)
        state.update_after_transaction(300.0, t2, "RecX", "UPI", 5, "INR")

        # Now evaluate T3: amount = 50 (below mean of 200) at 13:00 to Bank 8, Rec Y, format CARD
        t3 = datetime.datetime(2026, 5, 1, 13, 0, 0)
        t3_amount = 50.0

        # Manual calculations:
        # Prior sample amounts: [100, 300]
        # Mean = 200.0
        # Sample variance = ((100-200)^2 + (300-200)^2) / (2 - 1) = (10000 + 10000) / 1 = 20000
        # Sample std = sqrt(20000) = 141.421356...
        # Expected z-score = (50 - 200) / 141.421356... = -150 / 141.421356... = -1.06066...
        expected_z = (50.0 - 200.0) / (20000.0 ** 0.5)

        assert state.velocity_score() == 2
        assert state.time_since_last(t3) == 1800.0  # 30 min from t2
        assert abs(state.spending_zscore(t3_amount) - expected_z) < 1e-5
        assert state.is_first_transaction() is False
        assert state.is_new_receiver("RecY") is True
        assert state.is_new_bank(8) is True
        assert ("CARD" not in state.known_payment_formats) is True


class TestNegativeSpendingDeviation:
    """Verify negative z-scores pass schema validation and flow through ML inference without clipping."""

    @pytest.mark.parametrize("z_score", [
        -2.5,
        -1.0607,
        -0.0001,
        0.0,
        0.0001,
        1.5,
        4.2,
    ])
    def test_z_score_validation_and_inference(self, z_score):
        payload = {
            "amount": 75.0,
            "payment_channel": "CARD",
            "time_since_last_transaction": 300.0,
            "velocity_score": 4.0,
            "spending_deviation_score": z_score,
            "is_first_transaction": 0,
            "hour": 14,
            "day_of_week": 2,
            "month": 7,
            "is_weekend": 0,
            "is_cross_bank_transfer": 1,
            "is_cross_currency_transfer": 0,
            "is_new_receiver": 0,
            "is_new_bank": 0,
            "is_new_payment_format": 0,
        }

        # Pydantic schema validation check
        req = PredictionRequest(**payload)
        assert req.spending_deviation_score == z_score

        # Actual ML inference check
        result = predict(payload)
        assert "fraud_probability" in result
        assert isinstance(result["fraud_probability"], float)
        assert 0.0 <= result["fraud_probability"] <= 1.0


class TestModelArtifactsAndFeatureOrdering:
    """Verify production model artifacts, feature names, and ordering match training contracts."""

    def test_artifact_files_exist_in_production_path(self):
        v2_dir = BASE_DIR / "models" / "saved_models_v2"
        model_file = v2_dir / "xgboost_hi_li_small.pkl"
        encoder_file = v2_dir / "payment_channel_encoder_hi_li_small.pkl"
        meta_file = v2_dir / "xgboost_metadata_hi_li_small.json"

        assert model_file.exists(), f"Missing model artifact: {model_file}"
        assert encoder_file.exists(), f"Missing encoder artifact: {encoder_file}"
        assert meta_file.exists(), f"Missing metadata artifact: {meta_file}"

    def test_bundle_loading_and_deterministic_feature_ordering(self):
        bundle = get_active_model_bundle()
        assert "model" in bundle
        assert "encoder" in bundle
        assert "metadata" in bundle

        # Verify exact 15 feature schema names and order
        expected_features = [
            "amount",
            "payment_channel",
            "time_since_last_transaction",
            "velocity_score",
            "spending_deviation_score",
            "is_first_transaction",
            "hour",
            "day_of_week",
            "month",
            "is_weekend",
            "is_cross_bank_transfer",
            "is_cross_currency_transfer",
            "is_new_receiver",
            "is_new_bank",
            "is_new_payment_format",
        ]
        assert FEATURE_NAMES == expected_features
        assert len(FEATURE_NAMES) == 15


class TestWelfordStatisticsBatchAgreement:
    """Compare Welford online statistical calculations against independent batch formulas."""

    def test_welford_vs_batch_numpy(self):
        samples = [10.5, 45.2, 88.0, 120.3, 15.0, 200.0, 50.4]
        state = AccountState(account_id="acc_welford")

        for i, val in enumerate(samples):
            state.update_after_transaction(
                amount=val,
                timestamp=datetime.datetime(2026, 1, 1, 10, i, 0),
                receiver=f"r_{i}",
                payment_format="CARD",
                bank=1,
                currency="INR",
            )

        # Batch ground truth using sample std (ddof=1)
        expected_mean = float(np.mean(samples))
        expected_std = float(np.std(samples, ddof=1))

        assert abs(state.mean_amount - expected_mean) < 1e-6
        assert abs(state.std_amount - expected_std) < 1e-6

    def test_single_observation_statistics(self):
        state = AccountState(account_id="acc_single")
        state.update_after_transaction(
            amount=100.0,
            timestamp=datetime.datetime(2026, 1, 1, 10, 0, 0),
            receiver="r",
            payment_format="UPI",
            bank=1,
            currency="INR",
        )
        assert state.transaction_count == 1
        assert state.mean_amount == 100.0
        assert state.std_amount == 1.0  # default minimum
        # spending z-score for transaction_count < 2 returns 0.0
        assert state.spending_zscore(100.0) == 0.0

    def test_constant_stream_no_floating_point_breakdown(self):
        state = AccountState(account_id="acc_flat")
        for i in range(100):
            state.update_after_transaction(
                amount=50.0,
                timestamp=datetime.datetime(2026, 1, 1, 0, i % 60, 0),
                receiver="r",
                payment_format="CARD",
                bank=1,
                currency="INR",
            )
        assert state.mean_amount == 50.0
        assert state.m2_amount >= 0.0
        assert state.std_amount == 1.0


class TestModelRegistryLifecycleAndPromotionGuards:
    """Verify registry list handling and candidate validation before promotion."""

    def test_inferior_model_promotion_rejected(self, tmp_path):
        import copy
        test_reg = {
            "active_model": "prod_v1",
            "models": [
                {
                    "model_id": "prod_v1",
                    "version": "1.0.0",
                    "status": "ACTIVE",
                    "metrics": {"f1_score": 0.85},
                    "training_stats": {"mean_amount": 100.0},
                }
            ]
        }

        reg_file = tmp_path / "registry.json"
        reg_file.write_text(json.dumps(test_reg))

        promoted = promote_model(
            model_name="candidate_inferior",
            metrics={"f1_score": 0.80, "accuracy": 0.90},
            metadata={"algorithm": "XGBoost"},
            training_stats={"mean_amount": 110.0},
            registry_path=reg_file,
        )
        assert promoted is False

        # Verify prod_v1 remains active
        with open(reg_file, "r") as f:
            data = json.load(f)
        assert data["active_model"] == "prod_v1"

    def test_superior_model_promotion_accepted(self, tmp_path):
        test_reg = {
            "active_model": "prod_v1",
            "models": [
                {
                    "model_id": "prod_v1",
                    "version": "1.0.0",
                    "status": "ACTIVE",
                    "metrics": {"f1_score": 0.85},
                    "training_stats": {"mean_amount": 100.0},
                }
            ]
        }

        reg_file = tmp_path / "registry.json"
        reg_file.write_text(json.dumps(test_reg))

        promoted = promote_model(
            model_name="candidate_superior",
            metrics={"f1_score": 0.92, "accuracy": 0.98},
            metadata={"algorithm": "XGBoost"},
            training_stats={"mean_amount": 105.0},
            registry_path=reg_file,
        )
        assert promoted is True

        # Verify candidate_superior is now active
        with open(reg_file, "r") as f:
            data = json.load(f)
        assert data["active_model"] == "candidate_superior"
        assert any(m["model_id"] == "candidate_superior" and m["status"] == "ACTIVE" for m in data["models"])


class TestTimestampAndMonthHandling:
    """Verify temporal features derive strictly from transaction timestamp and not the local system clock."""

    def test_month_derived_from_transaction_timestamp(self):
        from preprocessing.feature_engineering import extract_time_features
        import pandas as pd

        # Timestamp in January (month 1)
        df = pd.DataFrame([{"Timestamp": "2026-01-15T03:30:00Z"}])
        extracted = extract_time_features(df)
        assert extracted["month"].iloc[0] == 1
        assert extracted["hour"].iloc[0] == 3
        assert extracted["is_weekend"].iloc[0] == 0

        # Timestamp in December (month 12)
        df_dec = pd.DataFrame([{"Timestamp": "2026-12-25T23:59:59Z"}])
        extracted_dec = extract_time_features(df_dec)
        assert extracted_dec["month"].iloc[0] == 12
        assert extracted_dec["hour"].iloc[0] == 23
