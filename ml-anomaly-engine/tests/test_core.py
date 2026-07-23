"""
Unit tests for ML Anomaly Engine modules.

Run with:
    pytest ml-anomaly-engine/tests/ -v
"""
import pytest
import sys
import os

# Ensure the ml-anomaly-engine root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestAuthModule:
    """Test JWT creation and verification."""

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
            "transaction_id": "txn_001",
            "amount": 150.00,
            "payment_type": "TRANSFER",
            "payment_channel": "online",
            "from_account": "ACC001",
            "to_account": "ACC002",
            "hour": 14,
            "day_of_week": 2,
            "is_weekend": 0,
            "account_age_days": 365,
            "from_account_balance": 5000.0,
            "to_account_balance": 2000.0,
            "amount_to_balance_ratio": 0.03,
        }
        req = PredictionRequest(**data)
        assert req.transaction_id == "txn_001"
        assert req.amount == 150.00

    def test_prediction_request_missing_required_field(self):
        from inference.schemas import PredictionRequest

        with pytest.raises(Exception):
            # Missing amount field
            PredictionRequest(
                transaction_id="txn_001",
                payment_type="TRANSFER",
            )


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
                    "version": "2.0",
                    "model_type": "XGBoost",
                    "status": "ACTIVE",
                    "accuracy": 0.97,
                    "precision": 0.91,
                    "recall": 0.88,
                    "f1_score": 0.89,
                    "created_at": "2025-01-01",
                    "updated_at": "2025-01-01",
                    "model_path": "models/saved_models_v2/xgboost_v2.pkl",
                    "description": "XGBoost v2 test",
                }
            ],
        }

        registry_file = tmp_path / "registry.json"
        registry_file.write_text(json.dumps(registry_data))

        registry = ModelRegistry(registry_file)
        active = registry.get_active_model()
        assert active["model_id"] == "xgboost_v2"

    def test_list_models(self, tmp_path):
        import json
        from services.model_registry import ModelRegistry

        registry_data = {
            "active_model": "xgboost_v2",
            "models": [
                {
                    "model_id": "xgboost_v2",
                    "version": "2.0",
                    "model_type": "XGBoost",
                    "status": "ACTIVE",
                    "accuracy": 0.97,
                    "precision": 0.91,
                    "recall": 0.88,
                    "f1_score": 0.89,
                    "created_at": "2025-01-01",
                    "updated_at": "2025-01-01",
                    "model_path": "models/saved_models_v2/xgboost_v2.pkl",
                    "description": "XGBoost v2 test",
                }
            ],
        }

        registry_file = tmp_path / "registry.json"
        registry_file.write_text(json.dumps(registry_data))

        registry = ModelRegistry(registry_file)
        models = registry.list_models()
        assert len(models) == 1
        assert models[0]["model_id"] == "xgboost_v2"
