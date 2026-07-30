# Kaggle Benchmark Notebook Specification

> [!NOTE]
> This document specifies the layout, architecture, and evaluation plan for the future production-grade Kaggle Notebook. Notebook implementation code is deferred to the notebook implementation phase.

---

## 1. Notebook Objective & Goal

Publish a high-visibility, production-grade Kaggle Benchmark Notebook showcasing:
1. End-to-end processing of stateful AML transaction features from Parquet.
2. Exploratory Data Analysis (EDA) on extreme class imbalance and graph relationships.
3. Anomaly detection benchmarking comparing **Isolation Forest** (unsupervised) and **XGBoost / LightGBM** (supervised).
4. Evaluation tailored for financial crime detection (PR-AUC, Recall @ Low False Positive Rate).

---

## 2. Notebook Structure & Content Outline

```
1. Title & Executive Summary
   ├── Problem domain (Anti-Money Laundering transaction fraud)
   └── Solution highlights (Stateful account profiling & zero-leakage pipeline)

2. Environment Setup & Data Loading
   ├── Memory-optimized Parquet ingestion using PyArrow / DuckDB
   └── Schema verification & split loading (train.parquet, valid.parquet, test.parquet)

3. Exploratory Data Analysis (EDA)
   ├── Class Imbalance Analysis (Fraud ratio ~0.104%)
   ├── Monetary Spending Deviation Analysis (Z-score distributions)
   ├── Temporal Velocity & Time-delta Analysis
   └── Relationship & Network Transfer Features (Cross-bank / FX analysis)

4. Stateful Behavioral Feature Importance
   ├── Correlation heatmaps
   └── Feature ranking via Mutual Information & Tree Importance

5. Model Training & Benchmarking
   ├── Model 1: Unsupervised Isolation Forest Baseline
   ├── Model 2: Supervised XGBoost Classifier (tuned with scale_pos_weight)
   └── Model 3: LightGBM Anomaly Engine

6. Model Evaluation & Financial Crime Metrics
   ├── Precision-Recall AUC (PR-AUC)
   ├── ROC-AUC & Confusion Matrices
   └── Detection Recall @ 0.1% False Positive Threshold

7. Operational Recommendations & Conclusion
   └── Deployment guidelines for streaming ingestion gateways
```

---

## 3. Evaluation Metrics & Constraints

- **Primary Metric**: Precision-Recall AUC (PR-AUC) — critical for highly imbalanced datasets.
- **Secondary Metric**: FPR @ 99% Recall (bounding alert fatigue for financial compliance teams).
- **Environment Constraints**:
  - CPU runtime limit: < 20 minutes on Kaggle kernel.
  - RAM consumption limit: < 8 GB peak memory.
  - Code hygiene: Type hints, clear docstrings, reproducible random seeds (`RANDOM_STATE = 42`).
