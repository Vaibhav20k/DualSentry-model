"""
Comprehensive production test suite for ML Anomaly Engine modules.

Run with:
    pytest tests/ -v
"""
import datetime
import os
import sys
import pytest

# Ensure the ml-anomaly-engine root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestAuthModule:
    """Test JWT creation, verification, and expiration."""

    def test_create_and_verify_token(self):
        from auth.auth import create_access_token, verify_token

        data = {"sub": "testuser", "role": "analyst"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        payload = verify_token(token)
        assert payload["sub"] == "testuser"
        assert payload["role"] == "analyst"

    def test_invalid_token_raises(self):
        from auth.auth import verify_token
        from jose import JWTError

        with pytest.raises(JWTError):
            verify_token("not.a.valid.token")


class TestSchemas:
    """Test Pydantic schema validation."""

    def test_prediction_request_valid(self):
        from inference.schemas import PredictionRequest

        data = {
            "amount": 150.00,
            "payment_channel": "CARD",
            "time_since_last_transaction": 120.0,
            "velocity_score": 3.0,
            "spending_deviation_score": -0.45,  # Valid negative z-score
            "is_first_transaction": 0,
            "hour": 14,
            "day_of_week": 2,
            "month": 5,
            "is_weekend": 0,
            "is_cross_bank_transfer": 0,
            "is_cross_currency_transfer": 0,
            "is_new_receiver": 0,
            "is_new_bank": 0,
            "is_new_payment_format": 0,
        }
        req = PredictionRequest(**data)
        assert req.amount == 150.00
        assert req.payment_channel == "CARD"
        assert req.spending_deviation_score == -0.45

    def test_prediction_request_missing_required_field(self):
        from inference.schemas import PredictionRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            PredictionRequest(
                amount=100.0,
                # Missing payment_channel and other required fields
            )

    def test_prediction_request_invalid_channel(self):
        from inference.schemas import PredictionRequest
        from pydantic import ValidationError

        data = {
            "amount": 150.00,
            "payment_channel": "INVALID_CHANNEL",
            "time_since_last_transaction": 120.0,
            "velocity_score": 1.0,
            "spending_deviation_score": 0.0,
            "is_first_transaction": 0,
            "hour": 12,
            "day_of_week": 1,
            "month": 6,
            "is_weekend": 0,
            "is_cross_bank_transfer": 0,
            "is_cross_currency_transfer": 0,
            "is_new_receiver": 0,
            "is_new_bank": 0,
            "is_new_payment_format": 0,
        }
        with pytest.raises(ValidationError):
            PredictionRequest(**data)


class TestAccountState:
    """Audit stateful behavioral feature calculation."""

    def test_first_transaction(self):
        from preprocessing.account_state import AccountState

        state = AccountState(account_id="acc_001")
        assert state.is_first_transaction() is True
        assert state.velocity_score() == 0
        assert state.spending_zscore(500.0) == 0.0
        assert state.is_new_receiver("rec_001") is True
        assert state.is_new_bank(10) is True

    def test_welford_statistics_and_zscore(self):
        from preprocessing.account_state import AccountState

        state = AccountState(account_id="acc_001")
        now = datetime.datetime(2026, 1, 1, 10, 0, 0)

        # First transaction: amount = 100
        state.update_after_transaction(
            amount=100.0,
            timestamp=now,
            receiver="rec_001",
            payment_format="CARD",
            bank=1,
            currency="INR",
        )

        assert state.transaction_count == 1
        assert state.is_first_transaction() is False
        assert state.velocity_score() == 1
        assert state.is_new_receiver("rec_001") is False
        assert state.is_new_receiver("rec_002") is True

        # Second transaction: amount = 200
        later = datetime.datetime(2026, 1, 1, 10, 30, 0)
        assert state.time_since_last(later) == 1800.0

        state.update_after_transaction(
            amount=200.0,
            timestamp=later,
            receiver="rec_002",
            payment_format="UPI",
            bank=2,
            currency="INR",
        )

        assert state.transaction_count == 2
        assert state.mean_amount == 150.0
        # std for [100, 200] is sqrt(((100-150)^2 + (200-150)^2)/1) = sqrt(5000) ~= 70.71
        assert abs(state.std_amount - (5000.0 ** 0.5)) < 1e-4

        # Z-score for amount 150 (mean) is 0
        assert abs(state.spending_zscore(150.0)) < 1e-4
        # Z-score for amount 220.71 is ~ 1.0
        assert abs(state.spending_zscore(150.0 + (5000.0 ** 0.5)) - 1.0) < 1e-4
        # Negative Z-score for amount below average
        assert state.spending_zscore(50.0) < 0.0

    def test_constant_amount_zero_variance(self):
        from preprocessing.account_state import AccountState

        state = AccountState(account_id="acc_const")
        now = datetime.datetime(2026, 1, 1, 12, 0, 0)

        for _ in range(5):
            state.update_after_transaction(
                amount=50.0,
                timestamp=now,
                receiver="rec_fixed",
                payment_format="CARD",
                bank=1,
                currency="USD",
            )

        # Standard deviation should be protected against division by zero (minimum 1.0)
        assert state.std_amount >= 1.0
        assert state.spending_zscore(50.0) == 0.0

    def test_out_of_order_timestamp_non_negative(self):
        from preprocessing.account_state import AccountState

        state = AccountState(account_id="acc_time")
        t2 = datetime.datetime(2026, 1, 1, 12, 0, 0)
        t1 = datetime.datetime(2026, 1, 1, 11, 0, 0)

        state.update_after_transaction(
            amount=100.0,
            timestamp=t2,
            receiver="rec",
            payment_format="CARD",
            bank=1,
            currency="INR",
        )

        # Out-of-order previous timestamp should not return negative seconds
        assert state.time_since_last(t1) >= 0.0


class TestModelRegistry:
    """Test model registry operations."""

    def test_registry_loads(self, tmp_path):
        import json
        from services.model_registry import ModelRegistry

        registry_data = {
            "active_model": "xgboost_v2",
            "models": [
                {
                    "model_id": "xgboost_v2",
                    "version": "2.0.0",
                    "algorithm": "XGBoost",
                    "status": "ACTIVE",
                    "description": "XGBoost model",
                    "path": "models/saved_models_v2",
                    "artifacts": {
                        "model": "xgboost_hi_li_small.pkl",
                        "encoder": "payment_channel_encoder_hi_li_small.pkl",
                        "metadata": "xgboost_metadata_hi_li_small.json",
                    },
                    "dataset_version": "v1",
                    "feature_schema_version": "v1",
                    "training_run_id": "r1",
                    "created_at": "2026-01-01",
                    "updated_at": "2026-01-01",
                    "metrics": {"f1_score": 0.89},
                    "training_stats": {"mean_amount": 100.0},
                }
            ],
        }

        registry_file = tmp_path / "registry.json"
        registry_file.write_text(json.dumps(registry_data))

        registry = ModelRegistry(str(registry_file))
        active = registry.get_active_model()
        assert active["model_id"] == "xgboost_v2"


class TestPredictorInference:
    """Test full inference execution."""

    def test_predict_execution(self):
        from inference.predictor import predict

        transaction = {
            "amount": 250.0,
            "payment_channel": "UPI",
            "time_since_last_transaction": 60.0,
            "velocity_score": 2.0,
            "spending_deviation_score": 0.1,
            "is_first_transaction": 0,
            "hour": 15,
            "day_of_week": 3,
            "month": 6,
            "is_weekend": 0,
            "is_cross_bank_transfer": 1,
            "is_cross_currency_transfer": 0,
            "is_new_receiver": 0,
            "is_new_bank": 0,
            "is_new_payment_format": 0,
        }

        res = predict(transaction)
        assert "fraud_probability" in res
        assert "confidence" in res
        assert "prediction" in res
        assert "threshold" in res
        assert "reason_codes" in res
        assert 0.0 <= res["fraud_probability"] <= 1.0
        assert 0.0 <= res["confidence"] <= 1.0

