# Kaggle Dataset & Notebook Publishing Checklist

Use this checklist to ensure all pre-flight quality checks pass before publishing the Kaggle Dataset and Notebook.

---

## 1. Dataset Generation & Validation Checklist

- [ ] **Production Code Preservation**: Confirm no files in `ml-anomaly-engine/` were modified or duplicated.
- [ ] **Dataset Execution**: Execute `kaggle/dataset/scripts/build_kaggle_dataset.py` to generate output Parquet files.
- [ ] **Parquet Files Verification**:
  - [ ] `training_dataset_hi_li_small.parquet` present in `kaggle/dataset/outputs/`.
  - [ ] `train.parquet` present in `kaggle/dataset/outputs/`.
  - [ ] `valid.parquet` present in `kaggle/dataset/outputs/`.
  - [ ] `test.parquet` present in `kaggle/dataset/outputs/`.
- [ ] **Automated Validation Run**: Execute `kaggle/dataset/validation/validate_dataset.py`.
- [ ] **Validation Reports Check**:
  - [ ] `validation_report.json` generated and shows `"overall_passed": true`.
  - [ ] `validation_report.md` generated with clean status.
- [ ] **Zero Nulls Check**: Confirm 0 missing values across all 15 engineered features.
- [ ] **Schema Match**: Confirm identical column order and data types across all 4 Parquet files.
- [ ] **Class Balance Verification**: Confirm ~0.104% fraud ratio across all splits.

---

## 2. Documentation & Metadata Checklist

- [ ] **Kaggle Public README**: Verify `kaggle/dataset/README.md` is complete with attribution, feature dictionary, and code samples.
- [ ] **Metadata Files**:
  - [ ] `kaggle/dataset/metadata/dataset-metadata.json` valid for Kaggle API upload.
  - [ ] `kaggle/dataset/metadata/metadata.json` contains full schema and versioning info.
  - [ ] `kaggle/dataset/metadata/schema.json` matches dataset column spec.
- [ ] **Docs Verification**:
  - [ ] `kaggle/docs/dataset_spec.md` updated.
  - [ ] `kaggle/docs/notebook_spec.md` updated.
  - [ ] `kaggle/dataset/docs/feature_dictionary.md` complete.
  - [ ] `kaggle/dataset/docs/data_lineage.md` complete.

---

## 3. Kaggle API Upload Steps

```bash
# Install Kaggle CLI if not installed
pip install kaggle

# Configure Kaggle API Credentials (~/.kaggle/kaggle.json)

# Create/Upload Dataset to Kaggle
kaggle datasets create -p kaggle/dataset/metadata/ -u
```

---

## 4. Final Post-Upload Verification

- [ ] Verify dataset renders correctly on Kaggle web interface.
- [ ] Test public downloading of `train.parquet` via Kaggle API / Python script.
- [ ] Verify licensing information (CC BY 4.0) displays properly on Kaggle dataset page.
