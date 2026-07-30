# IBM AML Stateful Behavioral Feature Engineering Dataset

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Format: Parquet](https://img.shields.io/badge/Format-Apache%20Parquet-blue.svg)](https://parquet.apache.org/)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)

## 📌 Dataset Overview

This dataset provides production-grade **stateful behavioral feature engineering** extracted from the synthetic IBM Anti-Money Laundering (AML) transaction datasets (`HI-Small_Trans.csv` and `LI-Small_Trans.csv`).

Traditional tabular fraud datasets often use global aggregates (e.g. mean transaction amount across all history), which introduces catastrophic **data leakage** from future transactions into past features. This dataset models financial transactions as an online streaming sequence. For every single transaction, features are calculated **strictly from historical account state** before the account state is updated.

---

## 🏛️ IBM AML Dataset Attribution

The raw transaction graph data originates from IBM Research:
- **Creators**: IBM Research (Synthetic Financial Datasets for Anti-Money Laundering).
- **Source Files**: `HI-Small_Trans.csv` (High In-degree/Out-degree topology) & `LI-Small_Trans.csv` (Low In-degree/Out-degree topology).
- **Domain**: Financial Crime & Anti-Money Laundering (AML) Anomaly Detection.

---

## ⚙️ Stateful Behavioral Feature Generation & Welford's Algorithm

To simulate real-world streaming ingestion gateways, each sender account maintains an `AccountState` object during processing:
- **Online Mean & Variance**: Tracks running mean and standard deviation of account spending using **Welford's Algorithm** for online updates without storing full transaction history.
- **Velocity Tracking**: Accumulates exact account transaction counts (`velocity_score`).
- **Dynamic Sets**: Maintains sets of previously seen beneficiary receivers, target bank IDs, payment channels, and transaction currencies.

---

## 🛡️ Target Leakage Prevention Strategy

Data leakage is strictly eliminated through an explicit two-stage order of execution per transaction:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Read Transaction (Account A -> Account B, Amount, Time)   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Compute Features using CURRENT AccountState(A)           │
│    (State reflects ONLY transactions t < current_time)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Append Feature Vector to Dataset Output                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Update AccountState(A) with Current Transaction          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Train / Validation / Test Split Methodology

The dataset is partitioned into reproducible, stratified splits maintaining exact class balance (~0.1% positive laundering fraud ratio):

| Partition | Filename | Row Count | Percentage | Fraud Ratio |
| :--- | :--- | :---: | :---: | :---: |
| **Combined** | `training_dataset_hi_li_small.parquet` | ~5,300,000 | 100.0% | ~0.104% |
| **Train** | `train.parquet` | ~3,710,000 | 70.0% | ~0.104% |
| **Validation** | `valid.parquet` | ~795,000 | 15.0% | ~0.104% |
| **Test** | `test.parquet` | ~795,000 | 15.0% | ~0.104% |

*Splitting performed via `sklearn.model_selection.train_test_split` with `random_state=42` and `stratify=df['is_fraud']`.*

---

## 📋 Feature Descriptions & Dictionary

The dataset contains 16 columns (15 engineered features + 1 target label):

### Monetary Features
- `amount` (`float64`): Transaction amount in USD equivalent.
- `spending_deviation_score` (`float64`): Z-score of transaction amount relative to sender account's historical spending mean and standard deviation:
  $$\text{spending\_deviation\_score} = \frac{\text{amount} - \mu_{\text{historical}}}{\sigma_{\text{historical}}}$$

### Temporal Features
- `hour` (`int64`): Hour of transaction (0 to 23).
- `day_of_week` (`int64`): Day of week (0 = Monday, 6 = Sunday).
- `month` (`int64`): Month of year (1 to 12).
- `is_weekend` (`int64`): 1 if transaction occurred on Saturday or Sunday, else 0.
- `time_since_last_transaction` (`float64`): Elapsed seconds since sender account's prior transaction.
- `velocity_score` (`int64`): Count of prior transactions executed by sender account.
- `is_first_transaction` (`int64`): 1 if sender's first transaction, else 0.

### Relationship & Graph Features
- `is_new_receiver` (`int64`): 1 if beneficiary account is seen for the first time by sender, else 0.
- `is_new_bank` (`int64`): 1 if beneficiary bank ID has never been transferred to by sender, else 0.
- `is_new_payment_format` (`int64`): 1 if payment channel is new for this sender, else 0.
- `is_cross_bank_transfer` (`int64`): 1 if `From Bank != To Bank`, else 0.
- `is_cross_currency_transfer` (`int64`): 1 if `Payment Currency != Receiving Currency`, else 0.

### Transaction Channel & Target
- `payment_channel` (`string`): Payment method format (e.g. ACH, Wire, Credit Card, Cheque).
- `is_fraud` (`int64`): Ground truth target label (1 = Laundering / Fraud, 0 = Legitimate).

---

## 💻 Example Loading Code

### Python (Pandas & PyArrow)
```python
import pandas as pd

# Load train, validation, and test splits
train_df = pd.read_parquet("kaggle/dataset/outputs/train.parquet")
valid_df = pd.read_parquet("kaggle/dataset/outputs/valid.parquet")
test_df = pd.read_parquet("kaggle/dataset/outputs/test.parquet")

print("Train shape:", train_df.shape)
print("Fraud ratio:", train_df["is_fraud"].mean())
```

### Python (Polars)
```python
import polars as pl

train_df = pl.read_parquet("kaggle/dataset/outputs/train.parquet")
print(train_df.glimpse())
```

### SQL (DuckDB)
```sql
SELECT 
    payment_channel,
    COUNT(*) AS total_tx,
    AVG(is_fraud) AS fraud_rate,
    AVG(spending_deviation_score) AS avg_spending_zscore
FROM 'kaggle/dataset/outputs/train.parquet'
GROUP BY payment_channel
ORDER BY fraud_rate DESC;
```

---

## 📖 Citation Information

If you use this dataset in your research or Kaggle notebooks, please cite:

```bibtex
@misc{ibm_aml_stateful_features_2026,
  title={IBM AML Stateful Behavioral Feature Engineering Dataset},
  author={Fintech Pipeline Engineering Team},
  year={2026},
  publisher={Kaggle},
  howpublished={\url{https://www.kaggle.com/datasets/fintechpipeline/ibm-aml-stateful-behavioral-features}}
}
```

---

## ⚖️ License Considerations

This dataset is distributed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**. Users are free to share and adapt the material for academic and commercial purposes, provided appropriate attribution is given to IBM Research for the underlying raw transaction dataset and the Fintech Pipeline project for feature engineering.
