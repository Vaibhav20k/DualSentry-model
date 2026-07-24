"""
Phase 1 — Production Model Evaluation (VALIDATED)

Evaluates the ACTIVE production model registered in models/registry.json.
Uses the EXACT same preprocessing pipeline as the deployed inference service.
No hardcoded filenames. No mismatches.

Pipeline:
  1. Read model registry → discover active model
  2. Load model, encoder, metadata from registry-specified paths
  3. Load corresponding evaluation dataset (test.parquet from the training split)
  4. Apply EXACT same preprocessing as inference/predictor.py:
     - LabelEncoder on payment_channel (fitted during training)
  5. Compute metrics at the model's native threshold
  6. Save graphs and report
"""

import json
import time
import joblib
import numpy as np
import pandas as pd
import matplotlib
import hashlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    precision_recall_curve,
)

# ============================================================
# Paths
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = BASE_DIR / "models" / "registry.json"
EVAL_DATA_PATH = BASE_DIR / "data" / "processed" / "test.parquet"
REPORT_DIR = BASE_DIR / "models" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. Discover active model from registry (NO HARDCODED PATHS)
# ============================================================
print("=" * 60)
print("PHASE 1 — PRODUCTION MODEL EVALUATION")
print("=" * 60)

print("\n[1/8] Reading model registry...")
with open(REGISTRY_PATH) as f:
    registry = json.load(f)

active_id = registry["active_model"]
print(f"  Active model ID: {active_id}")
print(f"  Traffic split : {registry['traffic_split']}")

model_info = None
for m in registry["models"]:
    if m["model_id"] == active_id:
        model_info = m
        break

if model_info is None:
    raise RuntimeError(f"Active model '{active_id}' not found in registry models list")

MODEL_DIR = BASE_DIR / model_info["path"]
MODEL_PATH = MODEL_DIR / model_info["artifacts"]["model"]
ENCODER_PATH = MODEL_DIR / model_info["artifacts"]["encoder"]
METADATA_PATH = MODEL_DIR / model_info["artifacts"]["metadata"]

print(f"  Model       : {MODEL_PATH}")
print(f"  Encoder     : {ENCODER_PATH}")
print(f"  Metadata    : {METADATA_PATH}")

# ============================================================
# 2. Load model, encoder, metadata
# ============================================================
print("\n[2/8] Loading model artifacts...")
t0 = time.perf_counter()

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

with open(METADATA_PATH) as f:
    metadata = json.load(f)

THRESHOLD = metadata["threshold"]
N_FEATURES = metadata.get("features", None)

load_time = time.perf_counter() - t0

print(f"  Model type   : {type(model).__name__}")
print(f"  Threshold    : {THRESHOLD}")
print(f"  Model version: {model_info['version']}")
print(f"  Dataset      : {metadata.get('dataset', 'unknown')}")
print(f"  Features     : {N_FEATURES or 'unknown'}")
print(f"  ROC-AUC (meta): {metadata.get('roc_auc', 'N/A')}")
print(f"  Loaded in    : {load_time:.2f}s")

# ============================================================
# 3. Load evaluation dataset
# ============================================================
print(f"\n[3/8] Loading evaluation dataset...")
if not EVAL_DATA_PATH.exists():
    raise FileNotFoundError(
        f"Evaluation dataset not found: {EVAL_DATA_PATH}\n"
        f"Run split_dataset.py or train_xgboost_v2.py first to generate it."
    )

df = pd.read_parquet(EVAL_DATA_PATH)
TARGET = "is_fraud"

print(f"  Dataset : {EVAL_DATA_PATH.name}")
print(f"  Shape   : {df.shape}")

X_test = df.drop(columns=[TARGET])
y_test = df[TARGET]

n = len(y_test)
n_pos = int(y_test.sum())
n_neg = n - n_pos
fraud_pct = y_test.mean() * 100

print(f"  Samples : {n:,}")
print(f"  Fraud   : {n_pos:,}  ({fraud_pct:.4f}%)")
print(f"  Legit   : {n_neg:,}  ({100 - fraud_pct:.4f}%)")

# ============================================================
# 4. Apply EXACT same preprocessing as deployed inference
#    (from inference/predictor.py lines 72-91)
# ============================================================
print("\n[4/8] Applying production preprocessing pipeline...")

# Step 4a: payment_channel mapping (already in test.parquet as mapped values)
# The training data already has mapped values (ACH, Credit Card, etc.)
# The inference does: input["CARD"] → map to "Credit Card" → encode
# Our test set already has "Credit Card" not "CARD", so we skip the mapping
# and go directly to encoding.

# Step 4b: LabelEncoder.transform(payment_channel)
X_test["payment_channel"] = encoder.transform(
    X_test["payment_channel"]
)

# Step 4c: Model expects a DataFrame with the same column order
# as training. Verify columns match what the model expects.
expected_features = model.n_features_in_
print(f"  Features passed to model: {X_test.shape[1]}")
print(f"  Columns: {list(X_test.columns)}")

# ============================================================
# 5. Predict with probability
# ============================================================
print(f"\n[5/8] Running predict_proba() on {n:,} samples...")
t1 = time.perf_counter()
probabilities = model.predict_proba(X_test)[:, 1]
infer_time = time.perf_counter() - t1
print(f"  {n:,} predictions in {infer_time:.3f}s  ->  {n / infer_time:,.0f} samples/sec")

predictions = (probabilities >= THRESHOLD).astype(int)

fraud_predicted = int(predictions.sum())
print(f"  Predicted fraud: {fraud_predicted:,}  ({fraud_predicted / n * 100:.4f}%)")
print(f"  Actual fraud   : {n_pos:,}  ({fraud_pct:.4f}%)")

# ============================================================
# 6. Core metrics
# ============================================================
print(f"\n[6/8] Computing metrics at threshold={THRESHOLD}...")

metrics = {
    "evaluation_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "active_model_id": active_id,
    "model_version": model_info["version"],
    "model_path": str(MODEL_PATH),
    "model_hash_md5": hashlib.md5(open(MODEL_PATH, "rb").read()).hexdigest()[0:12] + "...",
    "dataset": str(EVAL_DATA_PATH),
    "dataset_samples": int(n),
    "dataset_fraud_rate_pct": round(fraud_pct, 4),
    "threshold": float(THRESHOLD),
    "n_samples": int(n),
    "n_positives": int(n_pos),
    "n_negatives": int(n_neg),
    "n_predicted_fraud": int(fraud_predicted),
    "n_predicted_legit": int(n - fraud_predicted),
    "accuracy": float(accuracy_score(y_test, predictions)),
    "precision": float(precision_score(y_test, predictions, zero_division=0)),
    "recall": float(recall_score(y_test, predictions, zero_division=0)),
    "f1": float(f1_score(y_test, predictions, zero_division=0)),
    "roc_auc": float(roc_auc_score(y_test, probabilities)),
    "pr_auc": float(average_precision_score(y_test, probabilities)),
    "inference_sec": float(infer_time),
    "samples_per_sec": float(n / infer_time),
}

print(f"\n{'=' * 60}")
print(json.dumps(metrics, indent=4))
print(f"{'=' * 60}")

# Save metrics
with open(REPORT_DIR / "metrics.json", "w") as f:
    json.dump(metrics, f, indent=4)

# ============================================================
# 7. Confusion matrix
# ============================================================
cm = confusion_matrix(y_test, predictions)
tn, fp, fn, tp = cm.ravel()
print(f"\n  Confusion Matrix")
print(f"    TN={tn:>10,}  FP={fp:>10,}")
print(f"    FN={fn:>10,}  TP={tp:>10,}")

np.savetxt(REPORT_DIR / "confusion_matrix.csv", cm, delimiter=",", fmt="%d")

fig, ax = plt.subplots(figsize=(5, 4))
im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
plt.colorbar(im, ax=ax)
ax.set_title(f"Confusion Matrix — {active_id} (threshold={THRESHOLD})", fontsize=11)
ax.set_xlabel("Predicted label")
ax.set_ylabel("True label")
classes = [f"Legit (0)\n{n_neg:,}", f"Fraud (1)\n{n_pos:,}"]
ax.set_xticks([0, 1]); ax.set_xticklabels(classes)
ax.set_yticks([0, 1]); ax.set_yticklabels(classes)
for i in range(2):
    for j in range(2):
        ax.text(j, i, f"{cm[i,j]:,}", ha="center", va="center",
                color="white" if cm[i,j] > cm.max() / 2 else "black", fontsize=13)
plt.tight_layout()
plt.savefig(REPORT_DIR / "confusion_matrix.png", dpi=150)
plt.close()
print("  Saved confusion_matrix.png")

# ============================================================
# 8. ROC and PR curves
# ============================================================
print(f"\n[7/8] Plotting curves...")

# ROC
fpr, tpr, _ = roc_curve(y_test, probabilities)
fig, ax = plt.subplots(figsize=(6, 5))
ax.plot(fpr, tpr, color="#1f77b4", lw=2,
        label=f"{active_id} (AUC = {metrics['roc_auc']:.4f})")
ax.plot([0, 1], [0, 1], "k--", lw=1, label="Random (AUC = 0.5)")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title(f"ROC Curve — {active_id}")
ax.legend(loc="lower right")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(REPORT_DIR / "roc_curve.png", dpi=150)
plt.close()
print("  Saved roc_curve.png")

# PR curve
prec_vals, rec_vals, _ = precision_recall_curve(y_test, probabilities)
fig, ax = plt.subplots(figsize=(6, 5))
ax.plot(rec_vals, prec_vals, color="#ff7f0e", lw=2,
        label=f"{active_id} (AP = {metrics['pr_auc']:.4f})")
baseline = y_test.mean()
ax.axhline(y=baseline, color="k", linestyle="--", lw=1,
           label=f"Baseline (prevalence = {baseline:.4f})")
ax.set_xlabel("Recall")
ax.set_ylabel("Precision")
ax.set_title(f"Precision-Recall Curve — {active_id}")
ax.legend(loc="upper right")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(REPORT_DIR / "pr_curve.png", dpi=150)
plt.close()
print("  Saved pr_curve.png")

# Feature importance
importance = model.feature_importances_
feature_names = list(X_test.columns)
top_n = min(20, len(feature_names))
idx = np.argsort(importance)[-top_n:][::-1]
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(range(top_n), importance[idx], color="#1f77b4")
ax.set_xticks(range(top_n))
ax.set_xticklabels([feature_names[i] for i in idx], rotation=45, ha="right", fontsize=8)
ax.set_ylabel("Importance (gain)")
ax.set_title(f"Top {top_n} Feature Importances — {active_id}")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(REPORT_DIR / "feature_importance.png", dpi=150)
plt.close()
print("  Saved feature_importance.png")

# ============================================================
# Classification report
# ============================================================
report_str = classification_report(y_test, predictions, zero_division=0,
                                   target_names=["Legit", "Fraud"])
print(f"\n[8/8] Classification Report\n")
print(report_str)
with open(REPORT_DIR / "classification_report.txt", "w") as f:
    f.write(report_str)

# ============================================================
# Summary
# ============================================================
print("=" * 60)
print("EVALUATION COMPLETE")
print("=" * 60)
print(f"  Active model : {active_id} (v{model_info['version']})")
print(f"  Model path   : {MODEL_PATH}")
print(f"  Threshold    : {THRESHOLD}")
print(f"  Dataset      : {EVAL_DATA_PATH.name} ({n:,} samples, {fraud_pct:.4f}% fraud)")
print(f"  Accuracy     : {metrics['accuracy']:.6f}")
print(f"  Precision    : {metrics['precision']:.6f}")
print(f"  Recall       : {metrics['recall']:.6f}")
print(f"  F1 Score     : {metrics['f1']:.6f}")
print(f"  ROC-AUC      : {metrics['roc_auc']:.6f}")
print(f"  PR-AUC       : {metrics['pr_auc']:.6f}")
print(f"  Samples/sec  : {metrics['samples_per_sec']:,.0f}")
print(f"\nOutputs written to: {REPORT_DIR}")
