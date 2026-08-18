from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import config.settings as settings


def load_registry(registry_path: Path | str | None = None) -> dict:
    path = Path(registry_path or settings.REGISTRY_PATH)
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_registry(registry: dict, registry_path: Path | str | None = None) -> None:
    path = Path(registry_path or settings.REGISTRY_PATH)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(
            registry,
            file,
            indent=4,
        )


def promote_model(
    model_name: str,
    metrics: dict,
    metadata: dict,
    training_stats: dict,
    registry_path: Path | str | None = None,
) -> bool:

    registry = load_registry(registry_path)
    active_model_id = registry.get("active_model")

    current_model = None
    for m in registry.get("models", []):
        if m.get("model_id") == active_model_id:
            current_model = m
            break

    current_f1 = 0.0
    if current_model:
        current_f1 = current_model.get("metrics", {}).get(
            "f1_score",
            0.0,
        )

    new_f1 = metrics.get("f1_score", 0.0)

    if new_f1 <= current_f1 and current_f1 > 0:
        print(
            "New model did not outperform current model."
        )
        return False

    today = datetime.now().strftime("%Y-%m-%d")

    # Deactivate existing models
    for m in registry.get("models", []):
        m["status"] = "INACTIVE"

    new_model_entry = {
        "model_id": model_name,
        "version": datetime.now().strftime("%Y.%m.%d"),
        "algorithm": metadata.get("algorithm", "XGBoost"),
        "status": "ACTIVE",
        "description": "Retrained production fraud model",
        "path": "models/saved_models",
        "artifacts": {
            "model": f"{model_name}.joblib",
            "encoder": "payment_channel_encoder_hi_li_small.pkl",
            "metadata": "xgboost_metadata_hi_li_small.json",
        },
        "dataset_version": "production_live",
        "feature_schema_version": "v1",
        "training_run_id": f"run_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "created_at": today,
        "updated_at": today,
        "metrics": metrics,
        "training_stats": training_stats,
    }

    registry["models"].append(new_model_entry)
    registry["active_model"] = model_name
    if "traffic_split" in registry:
        registry["traffic_split"] = {model_name: 100}

    save_registry(registry, registry_path)

    print(
        f"{model_name} promoted successfully."
    )

    return True