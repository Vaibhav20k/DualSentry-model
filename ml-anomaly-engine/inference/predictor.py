import json
import joblib
import pandas as pd
from pathlib import Path

from monitoring.drift_monitor import DriftMonitor
from services.model_registry import ModelRegistry
from services.model_manager import ModelManager
from services.feature_validator import FeatureValidator
from services.explainer import FraudExplainer
from services.prediction_logger import PredictionLogger

# ==========================================================
# Project Paths & Services
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

registry = ModelRegistry(
    BASE_DIR / "models" / "registry.json"
)

model_manager = ModelManager(BASE_DIR)

DRIFT_MONITOR = DriftMonitor()

FEATURE_NAMES = [
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

PAYMENT_CHANNEL_MAPPING = {
    "CARD": "Credit Card",
    "NET_BANKING": "Wire",
    "UPI": "ACH",
    "WALLET": "Cash",
}


def get_active_model_bundle():
    """Retrieve or dynamically reload the currently active model."""
    try:
        active_info = registry.get_active_model()
        return model_manager.load_model(active_info["model_id"])
    except Exception as e:
        # Fallback to direct load from saved_models_v2 or saved_models
        for dir_name in ["models/saved_models_v2", "models/saved_models"]:
            model_p = BASE_DIR / dir_name / "xgboost_hi_li_small.pkl"
            enc_p = BASE_DIR / dir_name / "payment_channel_encoder_hi_li_small.pkl"
            meta_p = BASE_DIR / dir_name / "xgboost_metadata_hi_li_small.json"
            if model_p.exists() and enc_p.exists() and meta_p.exists():
                with open(meta_p, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                return {
                    "model": joblib.load(model_p),
                    "encoder": joblib.load(enc_p),
                    "metadata": meta,
                    "info": {"version": meta.get("version", "2.0.0"), "model_id": "xgboost_v2"},
                }
        raise RuntimeError(f"Failed to load active model bundle: {e}")


# Initialize active model bundle on startup
try:
    _initial_bundle = get_active_model_bundle()
    METADATA = _initial_bundle.get("metadata", {})
    MODEL_VERSION = _initial_bundle.get("info", {}).get("version", "2.0.0")
    THRESHOLD = METADATA.get("threshold", 0.9843)
    print(f"Model Loaded : {_initial_bundle.get('info', {}).get('model_id', 'xgboost_v2')}")
    print(f"Version      : {MODEL_VERSION}")
    print(f"Threshold    : {THRESHOLD}")
except Exception as e:
    print(f"Warning: Could not pre-cache active model bundle: {e}")
    METADATA = {"threshold": 0.9843}
    MODEL_VERSION = "2.0.0"
    THRESHOLD = 0.9843


def predict(transaction: dict):
    # Validate incoming transaction
    FeatureValidator.validate(transaction)

    DRIFT_MONITOR.update(transaction)

    reason_codes = FraudExplainer.generate_reason_codes(transaction)

    bundle = get_active_model_bundle()
    model = bundle["model"]
    encoder = bundle["encoder"]
    metadata = bundle["metadata"]
    model_version = bundle["info"].get("version", MODEL_VERSION)
    threshold = metadata.get("threshold", THRESHOLD)

    # Construct DataFrame with deterministic feature column ordering
    row = {k: transaction.get(k, 0) for k in FEATURE_NAMES}
    dataframe = pd.DataFrame([row], columns=FEATURE_NAMES)

    channel_val = dataframe["payment_channel"].iloc[0]
    mapped_channel = PAYMENT_CHANNEL_MAPPING.get(channel_val, channel_val)
    try:
        dataframe["payment_channel"] = encoder.transform([mapped_channel])
    except Exception:
        # Fallback for unseen payment channels
        dataframe["payment_channel"] = 0

    probability = model.predict_proba(dataframe)[0][1]
    prediction = probability >= threshold
    confidence = max(probability, 1.0 - probability)

    response = {
        "fraud_probability": round(float(probability), 4),
        "confidence": round(float(confidence), 4),
        "prediction": bool(prediction),
        "threshold": threshold,
        "model_version": model_version,
        "reason_codes": reason_codes,
    }

    PredictionLogger.log(
        transaction,
        response,
    )

    return response