# Kaggle Dataset Automated Validation Report

**Status**: ✅ PASSED  
**Timestamp**: `2026-07-29 10:51:19 UTC`  
**Execution Time**: `21.76s`

---

## 📊 Summary Dashboard

| Metric | Full Dataset | Train Split | Validation Split | Test Split |
| :--- | :---: | :---: | :---: | :---: |
| **Filename** | `training_dataset_hi_li_small.parquet` | `train.parquet` | `valid.parquet` | `test.parquet` |
| **Row Count** | 12,002,394 | 8,401,675 | 1,800,359 | 1,800,360 |
| **Percentage** | 100% | 70.0% | 15.0% | 15.0% |
| **Fraud Ratio** | **0.0728%** | **0.0728%** | **0.0728%** | **0.0729%** |
| **File Size (MB)** | 211.96 MB | 154.55 MB | 33.26 MB | 33.26 MB |
| **Validation Status** | ✅ | ✅ | ✅ | ✅ |

---

## 🛡️ Validation Checks Breakdown

- **Schema Matching Across Splits**: ✅ PASSED
- **Row Count Split Sum Integrity**: ✅ PASSED
- **Required Columns Existence**: ✅ 16 / 16 Present
- **Null Value Enforcement**: ✅ Zero Missing Values across all engineered features

---

## 🔒 File Hashes & Reproducibility (SHA256)

```
training_dataset_hi_li_small.parquet     : f679439380ac1915537742a50dcb42ac8376d54d07b1b27982fd6f4236fec34e
train.parquet                            : 7f68bface55adbcd25479f6919b4d301baac657d10705b4300774b2e2bdd4108
valid.parquet                            : f58765cdae75f04c3e9d903f1e637946a89918ec196c4ea6b279d4259fde9908
test.parquet                             : 43bc780bb7253f8d42d48b70c8934a5d5ad3853fa997d8d361fc645d7166718c
```

---

## 📋 Required Feature Schema Verification

| Feature Name | Category | Data Type | Null Count | Status |
| :--- | :--- | :--- | :---: | :---: |
| `amount` | Monetary | `float64` | 0 | ✅ Valid |
| `spending_deviation_score` | Monetary | `float64` | 0 | ✅ Valid |
| `hour` | Temporal | `int64` | 0 | ✅ Valid |
| `day_of_week` | Temporal | `int64` | 0 | ✅ Valid |
| `month` | Temporal | `int64` | 0 | ✅ Valid |
| `is_weekend` | Temporal | `int64` | 0 | ✅ Valid |
| `time_since_last_transaction` | Temporal | `float64` | 0 | ✅ Valid |
| `velocity_score` | Temporal | `int64` | 0 | ✅ Valid |
| `is_first_transaction` | Temporal | `int64` | 0 | ✅ Valid |
| `is_new_receiver` | Relationship | `int64` | 0 | ✅ Valid |
| `is_new_bank` | Relationship | `int64` | 0 | ✅ Valid |
| `is_new_payment_format` | Relationship | `int64` | 0 | ✅ Valid |
| `is_cross_bank_transfer` | Relationship | `int64` | 0 | ✅ Valid |
| `is_cross_currency_transfer` | Relationship | `int64` | 0 | ✅ Valid |
| `payment_channel` | Transaction | `str` | 0 | ✅ Valid |
| `is_fraud` | Target | `int64` | 0 | ✅ Valid |

---
*Generated automatically by `kaggle/dataset/validation/validate_dataset.py`*
