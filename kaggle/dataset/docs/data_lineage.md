# Data Lineage & Provenance Specification

This document details the data flow from raw IBM AML synthetic source files to the final Kaggle Dataset Parquet files.

---

## 🏗️ Lineage Architecture Diagram

```
[IBM AML Synthetic Raw CSVs]
 ├── HI-Small_Trans.csv (~475 MB)
 └── LI-Small_Trans.csv (~650 MB)
         │
         ▼ (Chunked Reading: 250,000 rows/chunk)
 [FeaturePipeline Engine]
         │
         ├── Chronological Account Sorting per chunk
         ├── Stateful Profile Lookup (AccountState)
         ├── Feature Vector Construction (Pre-Transaction State)
         └── Stateful Profile Update (Post-Transaction State)
         │
         ▼ (PyArrow Stream Writer)
 [kaggle/dataset/outputs/training_dataset_hi_li_small.parquet]
         │
         ▼ (Stratified 70/15/15 Reproducible Split: seed 42)
 ├── train.parquet (70% - ~3.7M rows)
 ├── valid.parquet (15% - ~800k rows)
 └── test.parquet  (15% - ~800k rows)
```

---

## 📄 Source Datasets

- **Origin**: IBM Anti-Money Laundering Synthetic Dataset (IBM Research).
- **Files**:
  - `HI-Small_Trans.csv`: High In-degree / High Out-degree topology small transaction dataset.
  - `LI-Small_Trans.csv`: Low In-degree / Low Out-degree topology small transaction dataset.
- **Raw Schema**:
  - `Timestamp`: Datetime ISO string
  - `From Bank`: Sender bank ID
  - `Account`: Sender account identifier
  - `To Bank`: Beneficiary bank ID
  - `Account.1`: Beneficiary account identifier
  - `Amount Paid`: Transaction value
  - `Payment Currency`: Currency of payment
  - `Receiving Currency`: Currency received
  - `Payment Format`: Payment channel
  - `Is Laundering`: Laundering label (0 or 1)

---

## ⚡ Transformation & State Accumulation

1. **Online Mean & Variance Tracking**:
   - Uses **Welford's Algorithm** inside `AccountState`:
     $$M_k = M_{k-1} + \frac{x_k - M_{k-1}}{k}$$
     $$S_k = S_{k-1} + (x_k - M_{k-1})(x_k - M_k)$$
   - Prevents catastrophic numerical cancellation and enables single-pass online statistics.

2. **Strict Leakage Prevention Guarantee**:
   - Step 1: Query `AccountState` using data from transaction $t_n$.
   - Step 2: Assemble feature dictionary for transaction $t_n$.
   - Step 3: Call `state.update_after_transaction(...)` to record $t_n$ into `AccountState`.
   - Result: Information from transaction $t_n$ is NEVER present in the state during feature extraction for $t_n$.

3. **Stratified Splitting**:
   - `sklearn.model_selection.train_test_split` with `random_state=42` and `stratify=df['is_fraud']`.
   - Maintains exact class imbalance ratio (~0.1% fraud) across training, validation, and testing partitions.
