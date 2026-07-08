import json
import joblib
import pandas as pd

from pathlib import Path


# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "models" / "saved_models"


# ==========================================================
# Load Artifacts
# ==========================================================

print("=" * 60)
print("Loading ML Artifacts...")
print("=" * 60)

PREPROCESSOR = joblib.load(
    MODEL_DIR / "preprocessor.pkl"
)

MODEL = joblib.load(
    MODEL_DIR / "xgboost_v1.pkl"
)

with open(
    MODEL_DIR / "xgboost_metadata.json",
    "r",
) as f:

    METADATA = json.load(f)

THRESHOLD = METADATA["threshold"]

MODEL_VERSION = METADATA["version"]

print(f"Model Loaded : {MODEL_VERSION}")
print(f"Threshold    : {THRESHOLD}")


# ==========================================================
# Prediction
# ==========================================================

def predict(transaction: dict):

    dataframe = pd.DataFrame([transaction])

    processed = PREPROCESSOR.transform(
        dataframe
    )

    probability = MODEL.predict_proba(
        processed
    )[0][1]

    prediction = probability >= THRESHOLD

    return {
        "fraud_probability": round(
            float(probability),
            4,
        ),
        "prediction": bool(
            prediction,
        ),
        "threshold": THRESHOLD,
        "model_version": MODEL_VERSION,
    }