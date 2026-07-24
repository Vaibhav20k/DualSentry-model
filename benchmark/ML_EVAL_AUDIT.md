# ML Evaluation Audit — Complete Report

## Executive Summary

**The Phase 1 benchmark metrics are invalid.** The evaluation pipeline tested the **wrong model** against the **wrong data** using the **wrong threshold** with a **different preprocessing pipeline** than the deployed inference service.

Every metric in the Phase 1 report (Accuracy 26.93%, Precision 4.38%, Recall 92.8%, F1 0.0836, ROC-AUC 0.593) is a product of this mismatch and does not represent the production system.

---

## 1. DATASET

### What was evaluated
| Field | Value |
|-------|-------|
| **Filename** | `financial_fraud_detection_dataset.csv` |
| **Absolute path** | `ml-anomaly-engine/data/raw/financial_fraud_detection_dataset.csv` |
| **Total samples** | **5,000,000** (1,000,000 in test set) |
| **Fraud samples (test)** | 35,911 (3.59%) |
| **Normal samples (test)** | 964,089 (96.41%) |
| **Fraud percentage** | 3.59% |
| **Creation date** | Unknown (appears to be a public Kaggle-style dataset with engineered features) |
| **Synthetic?** | **YES** — contains pre-computed features like `spending_deviation_score`, `velocity_score`, `geo_anomaly_score` which are NOT raw transaction data |
| **Generated during benchmarking?** | **NO** — existed before benchmarking |
| **Randomly generated?** | Structured synthetic dataset (not randomly generated — has patterns) |
| **Kaggle data?** | **Highly likely** — 5M rows, 18 columns, synthetic fraud detection dataset widely available |
| **Same as training?** | **YES for V1, NO for V2** — V1 was trained on this. V2 was trained on HI-LI-Small AML data |

### What the production model was trained on
| Field | Value |
|-------|-------|
| **Source** | `HI-Small_Trans.csv` + `LI-Small_Trans.csv` (IBM AML dataset) |
| **Processed file** | `data/processed/training_dataset_hi_li_small.parquet` |
| **Total samples** | **12,002,394** |
| **Fraud samples** | 8,742 (**0.07%**) |
| **Fraud percentage** | 0.07% (vs 3.59% in eval data) |

---

## 2. TRAIN / TEST SPLIT

### V1 pipeline (`train_xgboost.py` source)
- **Created by:** `preprocess.py` (line 205-218)
- **Split method:** `sklearn.model_selection.train_test_split`
- **Random?** YES — `random_state=42`
- **Stratified?** YES — `stratify=y`
- **Time-based?** NO — purely random
- **Cross-validation?** Used during hyperparameter tuning (`StratifiedKFold` with 3 folds), but final eval is on the held-out 20% test set

### V2 pipeline (`train_xgboost_v2.py` source)
- **Created by:** `split_dataset.py`
- **Split method:** Two-stage `train_test_split`
- **Split:** 70% train, 15% validation, 15% test
- **Random?** YES — `random_state=42`
- **Stratified?** YES
- **Time-based?** NO

---

## 3. MODEL

| Property | Evaluated Model | Production (Live) Model |
|----------|----------------|------------------------|
| **Filename** | `xgboost.pkl` | `xgboost_hi_li_small.pkl` |
| **Directory** | `models/saved_models/` | `models/saved_models_v2/` |
| **Registry ID** | Not registered | `xgboost_v2` (ACTIVE, 100% traffic) |
| **Version** | v1 | 2.0.0 |
| **Features expected** | **38** (one-hot encoded) | **15** (raw) |
| **n_estimators** | 300 | 500 |
| **Creation** | From `train_xgboost.py` | From `train_xgboost_v2.py` on HI-LI-Small data |

**VERDICT: These are DIFFERENT models. The evaluation tested V1. Production serves V2.**

---

## 4. FEATURE PIPELINE

### Training preprocessing (`preprocess.py` — V1 pipeline)
```python
CATEGORICAL_COLUMNS = ["transaction_type", "merchant_category", "location", "device_used", "payment_channel"]
NUMERICAL_COLUMNS = ["amount", "time_since_last_transaction", "spending_deviation_score", "velocity_score",
                     "geo_anomaly_score", "hour", "day_of_week", "month", "is_weekend", "is_first_transaction"]
# Applies: StandardScaler + OneHotEncoder
# Result: 38 features (dense numpy array)
```

### Training preprocessing (`train_xgboost_v2.py` — V2/production pipeline)
```python
# Loads parquet file with 15 pre-computed features
# Applies: LabelEncoder on 'payment_channel' only
# No scaling. No other encoding.
# Result: 15 features (DataFrame)
```

### Inference preprocessing (`predictor.py` — deployed inference)
```python
# 1. Validate transaction
# 2. Create pandas DataFrame from dict
# 3. Map payment_channel: {"CARD": "Credit Card", "NET_BANKING": "Wire", "UPI": "ACH", "WALLET": "Cash"}
# 4. LabelEncoder.transform(payment_channel)
# 5. model.predict_proba(dataframe)  # DIRECTLY on raw features!
```

### MISMATCHES FOUND

| Aspect | Evaluation Pipeline | Production Inference | Mismatch? |
|--------|-------------------|---------------------|-----------|
| **Payment channel encoding** | OneHotEncoder (5 categories → 5 binary columns) | LabelEncoder + mapping (1 integer column) | **YES** |
| **Numerical scaling** | StandardScaler (z-score normalization) | NONE (raw values) | **YES** |
| **Feature count** | 38 features | 15 features | **YES** |
| **Feature engineering** | Extracts hour/day/month from timestamp | Expects pre-computed temporal features | **YES** |
| **Missing value handling** | Fills `time_since_last_transaction` with -1 | Assumes all values present | Different assumption |
| **`geo_anomaly_score`** | Used as feature | NOT in V2 model | **YES** |
| **`transaction_type`** | One-hot encoded | NOT in V2 model | **YES** |
| **`location`** | One-hot encoded | NOT in V2 model | **YES** |
| **`device_used`** | One-hot encoded | NOT in V2 model | **YES** |
| **`is_cross_bank_transfer`** | NOT in V1 | Used in V2 | **YES** |
| **`is_new_receiver`** | NOT in V1 | Used in V2 | **YES** |
| **`is_new_bank`** | NOT in V1 | Used in V2 | **YES** |
| **`is_new_payment_format`** | NOT in V1 | Used in V2 | **YES** |

**Total mismatches: 14+**

---

## 5. THRESHOLD

| Property | Evaluation | Production |
|----------|-----------|------------|
| **Threshold** | **0.36** | **0.9867** |
| **Source file** | `xgboost_metadata.json` | `xgboost_metadata_hi_li_small.json` |
| **Source path** | `models/saved_models/` | `models/saved_models_v2/` |
| **Derived from** | F1-optimization search over 0.05-0.95 (V1 pipeline) | F1-optimization on PR curve (V2 pipeline) |
| **Overridden?** | NO — used the threshold baked into the V1 metadata | NO — loaded from registry metadata |

The 0.36 threshold was the F1-optimal threshold for the V1 model on its test data. The 0.9867 threshold was the F1-optimal threshold for the V2 model on its validation set.

---

## 6. METRIC COMPUTATION

The evaluation script (`phase1_model_eval.py`) uses standard `sklearn.metrics`:
- `accuracy_score(y_test, predictions)` — line 97
- `precision_score(y_test, predictions, zero_division=0)` — line 98
- `recall_score(y_test, predictions, zero_division=0)` — line 99
- `f1_score(y_test, predictions, zero_division=0)` — line 100
- `roc_auc_score(y_test, probabilities)` — line 101
- `average_precision_score(y_test, probabilities)` — line 102
- `confusion_matrix(y_test, predictions)` — line 115

**Formulas are correct.** The computation itself is not the source of error.

---

## 7. CONFUSION MATRIX VERIFICATION

From `metrics.json`:
```
TN=235,971  FP=728,118
FN=2,587    TP=33,324
```

Verification:
- **Accuracy**: (235971 + 33324) / 1000000 = **0.2693** ✓
- **Precision**: 33324 / (33324 + 728118) = **0.0438** ✓
- **Recall**: 33324 / (33324 + 2587) = **0.9280** ✓
- **F1**: 2 * (0.0438 * 0.9280) / (0.0438 + 0.9280) = **0.0836** ✓

**Math checks out.** The confusion matrix and metrics are internally consistent.

---

## 8. LIVE MODEL VERIFICATION

80 live predictions through the production model (`POST /predict`):

| Metric | Value |
|--------|-------|
| **Threshold** | **0.9867** |
| **Total predictions** | 100 |
| **Fraud predicted** | **0 (0.0%)** |
| **Non-fraud predicted** | 100 (100.0%) |
| **Fraud prob (avg)** | 0.1469 |
| **Fraud prob (median)** | 0.0246 |
| **Fraud prob (max)** | 0.9845 |
| **Cases where prob ≥ 0.36** | 14 (14.0%) |
| **Cases where prob ≥ 0.9867** | 0 (0.0%) |

**The deployed model behaves COMPLETELY DIFFERENTLY from the evaluation.** It predicts 0% fraud (vs 34% in the evaluation). Even with the erroneous 0.36 threshold, only 14% of cases would be flagged — versus 76% in the evaluation.

---

## 9. DATA LEAAKGE

- **Train/test leakage:** Unlikely within each pipeline (stratified split). But the evaluation tested V1 model against V1 data, so leakage within that pipeline is not a factor.
- **Duplicate rows:** Not directly checked, but the V1 and V2 datasets are from completely different sources.
- **Label leakage:** The evaluation dataset contains pre-computed features that are SUSPICIOUS: `spending_deviation_score`, `velocity_score`, `geo_anomaly_score` are features that require a baseline/history to compute — effectively encoding label information into the features.
- **Future information:** Not applicable (random split).
- **Incorrect target column:** Target column `is_fraud` is consistent in both pipelines.

---

## 10. PREPROCESSING MISMATCH

**Yes, the evaluation pipeline uses COMPLETELY DIFFERENT preprocessing than the deployed inference pipeline.**

See Section 4 above for the complete list of 14+ mismatches.

---

## 11. REPRODUCIBILITY

Re-running the evaluation as-is would produce the **same metrics** because:
1. The data (`X_test.pkl`, `y_test.pkl`) is deterministic (pickled already)
2. The model (`xgboost.pkl`) is deterministic
3. The script uses `predict_proba` with fixed threshold 0.36

The metrics are **reproducible but meaningless** for the production system.

---

## 12. FINAL CONCLUSION

| Question | Answer |
|----------|--------|
| **1. Were these metrics produced from the production model?** | **NO.** The evaluation tested `xgboost.pkl` (V1, 38 features, threshold 0.36). Production serves `xgboost_hi_li_small.pkl` (V2, 15 features, threshold 0.9867). These are completely different models. |
| **2. Were they produced using synthetic data?** | **YES.** `financial_fraud_detection_dataset.csv` is a synthetic dataset with pre-computed features. Additionally, the V1 model's test data (from the same file) was processed with a StandardScaler+OneHotEncoder pipeline that does not match the deployed inference preprocessing at all. |
| **3. Is the evaluation trustworthy?** | **NO.** Every metric is invalid for the deployed system because of three independent failures: (a) wrong model, (b) wrong data, (c) wrong preprocessing pipeline. |
| **4. What is the root cause?** | **The Phase 1 evaluation script (`benchmark/phase1_model_eval.py`) was hardcoded to load `models/saved_models/xgboost.pkl` and `data/processed/X_test.pkl` — files from the V1 training pipeline. It did not consult the model registry to discover which model was actually deployed, and did not use the same preprocessing as the production inference code.** Specifically: the evaluation loads from `Path("models/saved_models/xgboost.pkl")` but the registry says the active model is at `models/saved_models_v2/xgboost_hi_li_small.pkl`. The evaluation loads from `data/processed/X_test.pkl` (38 features, sklearn pipeline output), but the production model expects 15 raw features with only a LabelEncoder on payment_channel. |

### Root cause chain:
```
eval_model_path = MODEL_DIR / "xgboost.pkl"                     # ← Hardcoded to V1
eval_data_path  = PROC_DIR / "X_test.pkl"                       # ← Hardcoded to V1 data
eval_threshold  = meta["threshold"] = 0.36                      # ← V1's threshold
```
**Should have been:**
```
registry        = ModelRegistry("models/registry.json")          # ← Check what's live
active_model    = registry.get_active_model()                    # → xgboost_v2 → xgboost_hi_li_small.pkl
model_path      = registry.get_active_model_path()               # → models/saved_models_v2/
eval_data       = pd.read_parquet("data/processed/test.parquet") # → V2's test split
eval_threshold  = v2_metadata["threshold"] = 0.9867              # → V2's threshold
```
