from __future__ import annotations

import os
from pathlib import Path

# =====================================================
# Base Paths
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = BASE_DIR / "models" / "saved_models"
REGISTRY_PATH = BASE_DIR / "models" / "registry.json"

# =====================================================
# Database Configuration
# =====================================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "fintech_db")
DB_USER = os.getenv("DB_USER", "fintech_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dev_password_change_in_prod")

# =====================================================
# Model Configuration
# =====================================================

DRIFT_THRESHOLD = float(
    os.getenv("DRIFT_THRESHOLD", "0.20")
)

TRAIN_TEST_SPLIT = float(
    os.getenv("TRAIN_TEST_SPLIT", "0.20")
)

RANDOM_STATE = int(
    os.getenv("RANDOM_STATE", "42")
)

MODEL_FILE_EXTENSION = ".joblib"