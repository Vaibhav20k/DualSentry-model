# 🤖 ML Pipeline Documentation

## Overview

The ML Anomaly Engine uses a **XGBoost** classifier trained on the IBM Transactions for Anti Money Laundering (AML) dataset to detect fraudulent financial transactions in real-time.

---

## Dataset

| Dataset | Source | Transactions |
|---|---|---|
| HI-Small | IBM AML (High Illicit ratio, small) | ~5,000 |
| HI-Medium | IBM AML (High Illicit ratio, medium) | ~50,000 |
| HI-Large | IBM AML (High Illicit ratio, large) | ~500,000 |
| LI-Small | IBM AML (Low Illicit ratio, small) | ~5,000 |

The model is trained on a curated subset to balance training speed and coverage.

---

## Feature Engineering

| Feature | Description | Source |
|---|---|---|
| `amount` | Transaction amount | Raw |
| `payment_type` | TRANSFER, CASH_IN, etc. (encoded) | Raw |
| `payment_channel` | online, mobile, branch (encoded) | Raw |
| `hour` | Hour of day (0–23) | Derived |
| `day_of_week` | Day (0=Mon, 6=Sun) | Derived |
| `is_weekend` | Binary weekend flag | Derived |
| `account_age_days` | Age of from-account in days | Baseline |
| `from_account_balance` | Sender's current balance | Baseline |
| `to_account_balance` | Receiver's current balance | Baseline |
| `amount_to_balance_ratio` | `amount / from_account_balance` | Derived |

---

## Preprocessing Pipeline

```
Raw CSV
   │
   ▼
Drop irrelevant columns
   │
   ▼
Parse timestamps → hour, day_of_week, is_weekend
   │
   ▼
Encode categorical features (payment_type, payment_channel)
   │
   ▼
StandardScaler on numerical features
   │
   ▼
Train/Validation/Test split (60/20/20)
   │
   ▼
Save preprocessor.pkl and scaler.pkl
```

---

## Model Training

### XGBoost v2

```python
XGBClassifier(
    scale_pos_weight=class_weight,   # handles class imbalance
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="auc",
    tree_method="hist",
    device="cpu",
)
```

Training approach:
- `RandomizedSearchCV` for hyperparameter tuning
- `StratifiedKFold` cross-validation to preserve class balance
- Optimal threshold search on validation set (maximizes F1)

### Isolation Forest (Unsupervised baseline)

An Isolation Forest is also trained as an unsupervised anomaly detection baseline for comparison.

---

## Model Performance

| Model | Accuracy | Precision | Recall | F1 Score | AUC-ROC |
|---|---|---|---|---|---|
| XGBoost v2 | ~97% | ~91% | ~88% | ~89% | ~0.98 |
| Isolation Forest | ~85% | ~72% | ~81% | ~76% | ~0.91 |

---

## Model Registry

The model registry is a JSON file at `models/registry.json`.

```json
{
  "active_model": "xgboost_v2",
  "models": [
    {
      "model_id": "xgboost_v2",
      "version": "2.0",
      "status": "ACTIVE",
      "model_path": "models/saved_models_v2/xgboost_v2.pkl",
      "accuracy": 0.97,
      "f1_score": 0.89,
      "created_at": "2025-01-01"
    }
  ]
}
```

### Hot Model Swap

Admins can activate any registered model without restarting the service:

```bash
curl -X POST http://localhost:8000/models/activate \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"model_id": "xgboost_v1"}'
```

---

## Automated Retraining Pipeline

The retraining pipeline (`retraining/retrain_pipeline.py`) can be triggered manually or on a schedule:

```bash
cd ml-anomaly-engine
python -m retraining.retrain_pipeline
```

**Steps:**
1. Load new transaction data from PostgreSQL
2. Run feature engineering pipeline
3. Train XGBoost with hyperparameter search
4. Evaluate against hold-out test set
5. Save model artifacts and update registry
6. Optionally activate new model if metrics improve

---

## Drift Detection

The `monitoring/drift_detector.py` module compares live inference feature distributions against the training distribution using:
- PSI (Population Stability Index) for numerical features
- Chi-squared test for categorical features

Drift is reported via the `/drift` endpoint and tracked in `ModelMonitor`.

---

## Audit Logging

All prediction requests are logged to `logs/audit.log` and `logs/predictions.jsonl` with:
- Username and role
- Action type (PREDICTION, LOGIN, ACTIVATE_MODEL, REGISTER_MODEL)
- Status (SUCCESS / FAILED)
- Timestamp
- Contextual details

---

## Training Scripts

| Script | Purpose |
|---|---|
| `training/preprocess.py` | Run full preprocessing pipeline |
| `training/split_dataset.py` | Train/val/test split |
| `training/train_xgboost.py` | XGBoost v1 training |
| `training/train_xgboost_v2.py` | XGBoost v2 training |
| `training/train_isolation_forest.py` | Isolation Forest training |
| `training/evaluate.py` | Evaluate model on test set |
| `retraining/retrain_pipeline.py` | Automated retraining pipeline |
