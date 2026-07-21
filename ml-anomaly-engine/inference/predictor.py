import json
import joblib
import pandas as pd

from pathlib import Path

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_ROOT = BASE_DIR / "models"

REGISTRY_PATH = MODELS_ROOT / "registry.json"

with open(REGISTRY_PATH, "r") as f:
    REGISTRY = json.load(f)

ACTIVE_MODEL = REGISTRY["active_model"]

MODEL_DIR = MODELS_ROOT / ACTIVE_MODEL

MODEL_INFO = REGISTRY["models"][ACTIVE_MODEL]

# ==========================================================
# Load Artifacts
# ==========================================================

print("=" * 60)
print("Loading ML Artifacts...")
print("=" * 60)

MODEL = joblib.load(
    MODEL_DIR / "xgboost_hi_li_small.pkl"
)

ENCODER = joblib.load(
    MODEL_DIR / "payment_channel_encoder_hi_li_small.pkl"
)

with open(
    MODEL_DIR / "xgboost_metadata_hi_li_small.json",
    "r",
) as f:
    METADATA = json.load(f)

THRESHOLD = METADATA["threshold"]

MODEL_VERSION = MODEL_INFO["version"]

print(f"Model Loaded : {MODEL_VERSION}")
print(f"Threshold    : {THRESHOLD}")

PAYMENT_CHANNEL_MAPPING = {
    "CARD": "Credit Card",
    "NET_BANKING": "Wire",
    "UPI": "ACH",
    "WALLET": "Cash",
}

# ==========================================================
# Prediction
# ==========================================================

def predict(transaction: dict):

    dataframe = pd.DataFrame([transaction])

    dataframe["payment_channel"] = (
    dataframe["payment_channel"]
    .map(PAYMENT_CHANNEL_MAPPING)
    .fillna(dataframe["payment_channel"])
    )

    dataframe["payment_channel"] = ENCODER.transform(
        dataframe["payment_channel"]
    )

    probability = MODEL.predict_proba(
        dataframe
    )[0][1]

    prediction = probability >= THRESHOLD
    confidence = max(
        probability,
        1 - probability,
    )

    return {
        "fraud_probability": round(
            float(probability),
            4,
        ),
        "confidence": round(
            float(confidence),
            4,
        ),
        "prediction": bool(prediction),
        "threshold": THRESHOLD,
        "model_version": MODEL_VERSION,
    } 