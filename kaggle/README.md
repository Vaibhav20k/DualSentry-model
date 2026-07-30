# Kaggle Workspace: IBM AML Stateful Behavioral Feature Dataset & Benchmark

Welcome to the dedicated Kaggle workspace for the **Fintech Anti-Money Laundering (AML) Anomaly Detection Pipeline**.

This workspace is an isolated extension of the core production repository, designed specifically for packaging, documenting, validating, and publishing a production-grade Kaggle Dataset and future benchmark notebook.

---

## 🏛️ Architecture & Relationship to Production

```
fintech-pipeline/
├── ml-anomaly-engine/         <-- [SINGLE SOURCE OF TRUTH] Production Core
│   ├── preprocessing/          <-- FeaturePipeline, AccountState, etc.
│   └── data/raw/               <-- Raw IBM AML Trans.csv source files
└── kaggle/                     <-- [ISOLATED WORKSPACE] Kaggle Publishing Engine
    ├── dataset/                <-- Dataset scripts, metadata, validation, outputs
    ├── notebook/               <-- Notebook specifications & assets
    └── docs/                   <-- Specifications & publishing checklists
```

> [!IMPORTANT]
> **Single Source of Truth Principle**: The core production project (`ml-anomaly-engine/`) owns all feature engineering, state management, and preprocessing logic. The Kaggle workspace **consumes** these production components via direct import and does not duplicate, modify, or rewrite production code.

---

## 📂 Directory Structure

```
kaggle/
│
├── README.md                           # Main workspace overview & instructions
│
├── dataset/                            # Kaggle Dataset Publishing Package
│   ├── scripts/                        # Executable dataset generation pipeline
│   │   └── build_kaggle_dataset.py
│   ├── metadata/                       # JSON metadata & schemas for Kaggle API
│   │   ├── dataset-metadata.json
│   │   ├── metadata.json
│   │   └── schema.json
│   ├── validation/                     # Automated data validation suite
│   │   ├── validate_dataset.py
│   │   ├── validation_report.json
│   │   └── validation_report.md
│   ├── outputs/                        # Output Parquet datasets
│   │   ├── training_dataset_hi_li_small.parquet
│   │   ├── train.parquet
│   │   ├── valid.parquet
│   │   └── test.parquet
│   ├── docs/                           # Comprehensive data lineage & dictionary
│   │   ├── feature_dictionary.md
│   │   └── data_lineage.md
│   └── README.md                       # Kaggle-ready public dataset README
│
├── notebook/                           # Kaggle Notebook Workspace (Spec Phase)
│   ├── notebook.ipynb                  # Notebook placeholder
│   ├── markdown/                       # Notebook markdown chapters
│   ├── assets/                         # Visual assets & diagrams
│   └── figures/                        # Generated figures & plots
│
└── docs/                               # Technical Specifications & Guides
    ├── dataset_spec.md                 # Dataset pipeline technical specification
    ├── notebook_spec.md                # Kaggle notebook specification roadmap
    └── publishing_checklist.md         # Pre-flight publishing checklist
```

---

## 🚀 Quick Start Guide

### 1. Requirements & Prerequisites
Ensure you are using the Python environment configured for the production pipeline (which includes `pandas`, `pyarrow`, and `scikit-learn`):

```bash
# Windows PowerShell
.\ml-anomaly-engine\.venv\Scripts\python.exe kaggle\dataset\scripts\build_kaggle_dataset.py
```

### 2. Generating the Kaggle Datasets
Run the dataset generator script. It processes the IBM AML transactions in 250,000-row chunks, applies production stateful behavioral feature extraction using `FeaturePipeline`, and creates stratified train/validation/test splits:

```bash
python kaggle/dataset/scripts/build_kaggle_dataset.py
```

Outputs generated in `kaggle/dataset/outputs/`:
- `training_dataset_hi_li_small.parquet`: Combined feature dataset
- `train.parquet`: 70% stratified training split
- `valid.parquet`: 15% stratified validation split
- `test.parquet`: 15% stratified test split

### 3. Validating the Dataset
Run the automated validation suite to verify schema integrity, non-null guarantees, class distributions, and reproducibility:

```bash
python kaggle/dataset/validation/validate_dataset.py
```

View the generated `kaggle/dataset/validation/validation_report.md` for full health metrics.

---

## 📊 Dataset Highlights

- **Source Data**: IBM Synthetic AML Dataset (`HI-Small_Trans.csv` & `LI-Small_Trans.csv`).
- **Feature Count**: 15 Production-Grade Features (Monetary, Temporal, Relationship, Transaction, and Target).
- **Leakage Prevention**: Strictly historical `AccountState` tracking with Welford's algorithm for online variance/mean computation.
- **Format**: High-performance Apache Parquet with Snappy compression.

---

## 📜 Documentation & Specifications

- **[Dataset Technical Specification](file:///C:/Projects/fintech-pipeline/kaggle/docs/dataset_spec.md)**
- **[Kaggle Dataset Public README](file:///C:/Projects/fintech-pipeline/kaggle/dataset/README.md)**
- **[Feature Dictionary](file:///C:/Projects/fintech-pipeline/kaggle/dataset/docs/feature_dictionary.md)**
- **[Notebook Specification](file:///C:/Projects/fintech-pipeline/kaggle/docs/notebook_spec.md)**
- **[Publishing Checklist](file:///C:/Projects/fintech-pipeline/kaggle/docs/publishing_checklist.md)**
