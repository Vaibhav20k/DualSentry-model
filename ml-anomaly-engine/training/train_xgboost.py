import json
import joblib
import numpy as np
import pandas as pd

from pathlib import Path

from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
)

from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
)
from sklearn.utils import resample

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"

MODEL_DIR = BASE_DIR / "models" / "saved_models"

REPORT_DIR = BASE_DIR / "models" / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42

USE_SAMPLE = True
SAMPLE_SIZE = 1000000

# ==========================================================
# Load Dataset
# ==========================================================

def load_dataset():

    print("=" * 60)
    print("Loading Processed Dataset...")
    print("=" * 60)

    X_train = joblib.load(PROCESSED_DIR / "X_train.pkl")
    X_test = joblib.load(PROCESSED_DIR / "X_test.pkl")

    y_train = joblib.load(PROCESSED_DIR / "y_train.pkl")
    y_test = joblib.load(PROCESSED_DIR / "y_test.pkl")

    print("Train :", X_train.shape)
    print("Test  :", X_test.shape)

    return X_train, X_test, y_train, y_test


# ==========================================================
# Stratified Sample
# ==========================================================

def sample_dataset(X, y):

    if not USE_SAMPLE:
        return X, y

    print("\nUsing Stratified Sample...")

    idx = np.arange(len(y))

    sample_idx = resample(
        idx,
        replace=False,
        n_samples=SAMPLE_SIZE,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    return X[sample_idx], y.iloc[sample_idx]


# ==========================================================
# Build Base Model
# ==========================================================

def build_model(y_train):

    positives = y_train.sum()
    negatives = len(y_train) - positives

    scale_pos_weight = negatives / positives

    print(f"\nscale_pos_weight = {scale_pos_weight:.2f}")

    model = XGBClassifier(

        objective="binary:logistic",

        eval_metric="aucpr",

        tree_method="hist",

        random_state=RANDOM_STATE,

        n_jobs=-1,

        learning_rate=0.03,

        n_estimators=500,

        max_depth=6,

        subsample=0.8,

        colsample_bytree=0.8,

        gamma=0.2,

        min_child_weight=5,

        reg_alpha=0.1,

        reg_lambda=1.5,

        scale_pos_weight=scale_pos_weight,

    )

    return model
# ==========================================================
# Hyperparameter Search
# ==========================================================

def tune_model(
    model,
    X_train,
    y_train,
):

    print("\nStarting Hyperparameter Search...\n")

    param_grid = {

        "max_depth": [4, 6, 8],

        "learning_rate": [0.03, 0.05, 0.1],

        "subsample": [0.8, 0.9, 1.0],

        "colsample_bytree": [0.8, 0.9, 1.0],

        "min_child_weight": [3, 5, 7],

        "gamma": [0, 0.2, 0.5],

        "n_estimators": [300, 500, 700],

    }

    cv = StratifiedKFold(
    n_splits=3,
    shuffle=True,
    random_state=RANDOM_STATE,
    )

    search = RandomizedSearchCV(

        estimator=model,

        param_distributions=param_grid,

        n_iter=10,

        scoring="average_precision",

        cv=cv,

        verbose=2,

        random_state=RANDOM_STATE,

        n_jobs=-1,

    )

    search.fit(

        X_train,

        y_train,

    )

    print("\nBest Parameters")

    print(search.best_params_)

    print("\nBest Score")

    print(search.best_score_)

    return search.best_estimator_


# ==========================================================
# Train
# ==========================================================

def train_model(

    model,

    X_train,

    y_train,

):

    print("\nTraining Best Model...\n")

    model.fit(

        X_train,

        y_train,

    )

    return model


# ==========================================================
# Threshold Optimization
# ==========================================================

def find_best_threshold(

    model,

    X_test,

    y_test,

):

    print("\nFinding Best Threshold...\n")

    probabilities = model.predict_proba(

        X_test

    )[:, 1]

    best_threshold = 0.5

    best_f1 = 0

    for threshold in np.arange(

        0.05,

        0.96,

        0.01,

    ):

        predictions = (

            probabilities >= threshold

        ).astype(int)

        score = f1_score(

            y_test,

            predictions,

            zero_division=0,

        )

        if score > best_f1:

            best_f1 = score

            best_threshold = threshold

    print(

        f"Best Threshold : {best_threshold:.2f}"

    )

    print(

        f"Best F1        : {best_f1:.4f}"

    )

    return best_threshold


# ==========================================================
# Evaluation
# ==========================================================

def evaluate(

    model,

    X_test,

    y_test,

    threshold,

):

    print("\nEvaluating...\n")

    probabilities = model.predict_proba(

        X_test

    )[:, 1]

    predictions = (

        probabilities >= threshold

    ).astype(int)

    metrics = {

        "accuracy": float(

            accuracy_score(

                y_test,

                predictions,

            )

        ),

        "precision": float(

            precision_score(

                y_test,

                predictions,

                zero_division=0,

            )

        ),

        "recall": float(

            recall_score(

                y_test,

                predictions,

                zero_division=0,

            )

        ),

        "f1": float(

            f1_score(

                y_test,

                predictions,

                zero_division=0,

            )

        ),

        "roc_auc": float(

            roc_auc_score(

                y_test,

                probabilities,

            )

        ),

        "pr_auc": float(

            average_precision_score(

                y_test,

                probabilities,

            )

        ),

        "threshold": float(

            threshold

        ),

    }

    print(

        json.dumps(

            metrics,

            indent=4,

        )

    )

    cm = confusion_matrix(

        y_test,

        predictions,

    )

    np.savetxt(

        REPORT_DIR / "confusion_matrix.csv",

        cm,

        delimiter=",",

        fmt="%d",

    )

    with open(

        REPORT_DIR / "metrics.json",

        "w",

    ) as f:

        json.dump(

            metrics,

            f,

            indent=4,

        )

    print("\nClassification Report\n")

    print(

        classification_report(

            y_test,

            predictions,

            zero_division=0,

        )

    )

    return metrics

# ==========================================================
# Feature Importance
# ==========================================================

def save_feature_importance(model):

    print("\nSaving Feature Importance...")

    importance = model.feature_importances_

    importance_df = pd.DataFrame(
        {
            "feature_index": np.arange(len(importance)),
            "importance": importance,
        }
    )

    importance_df = importance_df.sort_values(
        by="importance",
        ascending=False,
    )

    importance_df.to_csv(
        REPORT_DIR / "feature_importance.csv",
        index=False,
    )

    print("Feature importance saved.")


# ==========================================================
# Save Model
# ==========================================================

def save_model(model, threshold):

    print("\nSaving Model...")

    joblib.dump(
        model,
        MODEL_DIR / "xgboost_v1.pkl",
    )

    metadata = {
        "model": "xgboost",
        "version": "v1",
        "threshold": float(threshold),
    }

    with open(
        MODEL_DIR / "xgboost_metadata.json",
        "w",
    ) as f:
        json.dump(
            metadata,
            f,
            indent=4,
        )

    print("Model saved successfully.")


# ==========================================================
# Main
# ==========================================================

def main():

    X_train, X_test, y_train, y_test = load_dataset()

    X_train, y_train = sample_dataset(
        X_train,
        y_train,
    )

    model = build_model(
        y_train,
    )

    model = tune_model(
        model,
        X_train,
        y_train,
    )

    model = train_model(
        model,
        X_train,
        y_train,
    )

    threshold = find_best_threshold(
        model,
        X_test,
        y_test,
    )

    evaluate(
        model,
        X_test,
        y_test,
        threshold,
    )

    save_feature_importance(
        model,
    )

    save_model(
        model,
        threshold,
    )

    print("\n" + "=" * 60)
    print("XGBoost Training Completed Successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()