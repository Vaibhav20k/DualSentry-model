from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier

from config.settings import (
    RANDOM_STATE,
    TRAIN_TEST_SPLIT,
)


def train_model(dataframe: pd.DataFrame) -> dict[str, Any]:

    X = dataframe.drop(columns=["prediction"])
    y = dataframe["prediction"]

    categorical_columns = [
        "payment_method",
        "location",
        "status",
    ]

    numerical_columns = [
        "amount",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_columns,
            ),
            (
                "numerical",
                "passthrough",
                numerical_columns,
            ),
        ]
    )

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),
            (
                "classifier",
                XGBClassifier(
                    random_state=RANDOM_STATE,
                    eval_metric="logloss",
                ),
            ),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TRAIN_TEST_SPLIT,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    pipeline.fit(
        X_train,
        y_train,
    )

    predictions = pipeline.predict(
        X_test,
    )

    probabilities = pipeline.predict_proba(
        X_test,
    )[:, 1]

    return {
        "model": pipeline,
        "X_test": X_test,
        "y_test": y_test,
        "predictions": predictions,
        "probabilities": probabilities,
        "metadata": {
            "algorithm": "XGBoost",
            "dataset_size": len(dataframe),
            "feature_columns": list(X.columns),
            "hyperparameters": {
                "random_state": RANDOM_STATE,
                "eval_metric": "logloss",
            },
        },
    }


if __name__ == "__main__":

    from retraining.dataset_builder import load_training_dataset
    from retraining.evaluator import evaluate_model

    dataframe = load_training_dataset()

    result = train_model(dataframe)

    metrics = evaluate_model(
        result["y_test"],
        result["predictions"],
        result["probabilities"],
    )

    logger = logging.getLogger(__name__)
    logger.info("Retraining metrics: %s", metrics)