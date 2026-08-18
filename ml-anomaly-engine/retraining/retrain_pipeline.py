from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from monitoring.drift_runner import run_drift_detection

from retraining.dataset_builder import (
    load_training_dataset,
)
from retraining.evaluator import (
    evaluate_model,
)
from retraining.model_saver import (
    save_model,
)
from retraining.registry_updater import (
    promote_model,
)
from retraining.trainer import (
    train_model,
)


def should_retrain():

    try:

        report = run_drift_detection()

    except RuntimeError as error:

        logger.warning("Drift detection failed: %s", error)

        return False

    return report["drift_detected"]


def retrain_pipeline():

    if not should_retrain():

        print("Retraining skipped.")

        return

    print("Loading dataset...")

    dataframe = load_training_dataset()

    print("Training model...")

    result = train_model(dataframe)

    print("Evaluating model...")

    metrics = evaluate_model(
        result["y_test"],
        result["predictions"],
        result["probabilities"],
    )

    import numpy as np

    probs = result["probabilities"]
    confidences = np.maximum(probs, 1.0 - probs)

    training_stats = {
        "mean_amount": float(dataframe["amount"].mean()),
        "mean_fraud_probability": float(probs.mean()),
        "mean_confidence": float(confidences.mean()),
        "fraud_rate": float(result["predictions"].mean()),
    }

    print(metrics)

    print("Saving model...")

    model_name = save_model(
        result["model"],
    )

    print(f"Saved as {model_name}")

    promote_model(
        model_name=model_name,
        metrics=metrics,
        metadata=result["metadata"],
        training_stats=training_stats,
    )


def main():

    retrain_pipeline()


if __name__ == "__main__":

    main()