from pathlib import Path

import joblib
import pandas as pd
import xgboost as xgb

from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
)

from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
    / "saved_models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)
print("=" * 60)
print("Loading datasets...")
print("=" * 60)

train = pd.read_parquet(
    DATA_DIR / "train.parquet"
)

valid = pd.read_parquet(
    DATA_DIR / "valid.parquet"
)

test = pd.read_parquet(
    DATA_DIR / "test.parquet"
)


TARGET = "is_fraud"

X_train = train.drop(
    columns=[TARGET]
)

y_train = train[TARGET]

X_valid = valid.drop(
    columns=[TARGET]
)

y_valid = valid[TARGET]

X_test = test.drop(
    columns=[TARGET]
)

y_test = test[TARGET]
encoder = LabelEncoder()

encoder.fit(
    X_train["payment_channel"]
)

X_train["payment_channel"] = encoder.transform(
    X_train["payment_channel"]
)

X_valid["payment_channel"] = encoder.transform(
    X_valid["payment_channel"]
)

X_test["payment_channel"] = encoder.transform(
    X_test["payment_channel"]
)

positive = y_train.sum()

negative = len(y_train) - positive

scale_pos_weight = negative / positive

print()

print(
    f"Scale Pos Weight = {scale_pos_weight:.2f}"
)
print()
print("=" * 60)
print("Training XGBoost...")
print("=" * 60)

model = xgb.XGBClassifier(

    objective="binary:logistic",

    eval_metric="aucpr",

    tree_method="hist",

    random_state=42,

    n_estimators=500,

    learning_rate=0.05,

    max_depth=8,

    subsample=0.8,

    colsample_bytree=0.8,

    scale_pos_weight=scale_pos_weight,

    early_stopping_rounds=30,
)

model.fit(

    X_train,

    y_train,

    eval_set=[
        (
            X_valid,
            y_valid,
        )
    ],

    verbose=20,
)
print()
print("=" * 60)
print("Evaluating...")
print("=" * 60)

probabilities = model.predict_proba(
    X_test
)[:, 1]
precision, recall, thresholds = precision_recall_curve(
    y_test,
    probabilities,
)

f1_scores = (
    2
    * precision[:-1]
    * recall[:-1]
) / (
    precision[:-1]
    + recall[:-1]
    + 1e-10
)

best_index = f1_scores.argmax()

best_threshold = thresholds[
    best_index
]

print()

print(
    f"Best Threshold : {best_threshold:.4f}"
)
predictions = (
    probabilities >= best_threshold
).astype(int)

print()

print(
    classification_report(
        y_test,
        predictions,
        digits=4,
    )
)

print()

print(
    confusion_matrix(
        y_test,
        predictions,
    )
)

print()

print(
    "ROC-AUC :",
    roc_auc_score(
        y_test,
        probabilities,
    ),
)

print(
    "PR-AUC  :",
    average_precision_score(
        y_test,
        probabilities,
    ),
)
joblib.dump(

    model,

    MODEL_DIR
    / "xgboost_hi_li_small.joblib",
)

joblib.dump(

    encoder,

    MODEL_DIR
    / "payment_channel_encoder_hi_li_small.joblib",
)

print()

print("=" * 60)
print("Model Saved Successfully")
print("=" * 60)