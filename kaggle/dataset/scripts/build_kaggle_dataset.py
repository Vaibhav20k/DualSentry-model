"""
kaggle/dataset/scripts/build_kaggle_dataset.py

Generates the Kaggle Dataset Parquet files using the core production FeaturePipeline
and AccountState implementations from ml-anomaly-engine/preprocessing.

Requirements:
- Consume production FeaturePipeline & AccountState (do not duplicate)
- Process IBM AML raw datasets (HI-Small_Trans.csv, LI-Small_Trans.csv) in 250,000-row chunks
- Maintain chronological ordering & stateful feature calculation without target leakage
- Produce deterministic outputs
- Generate training_dataset_hi_li_small.parquet, train.parquet, valid.parquet, test.parquet
  inside kaggle/dataset/outputs/
"""

import os
import sys
import time
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from sklearn.model_selection import train_test_split

# Setup Python path to import production ml-anomaly-engine components
SCRIPT_DIR = Path(__file__).resolve().parent
DATASET_DIR = SCRIPT_DIR.parent
KAGGLE_DIR = DATASET_DIR.parent
PROJECT_ROOT = KAGGLE_DIR.parent
ENGINE_DIR = PROJECT_ROOT / "ml-anomaly-engine"

if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from preprocessing.feature_pipeline import FeaturePipeline
from preprocessing.account_state import AccountState

INPUT_FILES = [
    "HI-Small_Trans.csv",
    "LI-Small_Trans.csv",
]

RAW_DATA_DIR = ENGINE_DIR / "data" / "raw"
OUTPUT_DIR = DATASET_DIR / "outputs"
FULL_DATASET_PATH = OUTPUT_DIR / "training_dataset_hi_li_small.parquet"
TRAIN_PATH = OUTPUT_DIR / "train.parquet"
VALID_PATH = OUTPUT_DIR / "valid.parquet"
TEST_PATH = OUTPUT_DIR / "test.parquet"

CHUNK_SIZE = 250_000
RANDOM_STATE = 42


def generate_full_dataset() -> Path:
    """
    Process raw CSV files in chunks using production FeaturePipeline
    and write to full dataset Parquet file.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("Starting Kaggle Dataset Generation Pipeline")
    print(f"Production Core Path : {ENGINE_DIR}")
    print(f"Raw Input Directory  : {RAW_DATA_DIR}")
    print(f"Output Directory     : {OUTPUT_DIR}")
    print("=" * 70)

    pipeline = FeaturePipeline()
    writer = None
    total_rows = 0
    start_time = time.time()

    try:
        for input_file in INPUT_FILES:
            input_path = RAW_DATA_DIR / input_file
            if not input_path.exists():
                raise FileNotFoundError(f"Input data file not found: {input_path}")

            print(f"\nProcessing source file: {input_file}")
            print("-" * 50)

            for chunk_idx, chunk in enumerate(pd.read_csv(input_path, chunksize=CHUNK_SIZE)):
                processed_chunk = pipeline.process_dataframe(chunk)

                table = pa.Table.from_pandas(processed_chunk, preserve_index=False)

                if writer is None:
                    writer = pq.ParquetWriter(FULL_DATASET_PATH, table.schema)

                writer.write_table(table)
                total_rows += len(processed_chunk)

                print(
                    f"  File: {input_file} | Chunk {chunk_idx + 1:02d} | "
                    f"Chunk Rows: {len(processed_chunk):>8,} | Cumulative: {total_rows:>10,}"
                )

    finally:
        if writer is not None:
            writer.close()

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("Full Combined Dataset Generation Complete")
    print(f"Total Rows Written : {total_rows:,}")
    print(f"Output File Path   : {FULL_DATASET_PATH}")
    print(f"Execution Time     : {elapsed / 60:.2f} minutes")
    print("=" * 70)

    return FULL_DATASET_PATH


def create_train_valid_test_splits(full_dataset_path: Path):
    """
    Perform reproducible stratified train/validation/test split (70/15/15).
    """
    print("\nCreating Reproducible Train / Validation / Test Splits (70 / 15 / 15)...")
    print("-" * 70)

    df = pd.read_parquet(full_dataset_path)
    total_samples = len(df)
    fraud_count = df["is_fraud"].sum()
    fraud_ratio = fraud_count / total_samples

    print(f"Total Dataset Samples : {total_samples:,}")
    print(f"Fraud Samples Count   : {fraud_count:,} ({fraud_ratio:.4%})")

    # 70% train, 30% temp (valid + test)
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=df["is_fraud"],
    )

    # 50% of temp = 15% of total for valid, 50% of temp = 15% of total for test
    valid_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=temp_df["is_fraud"],
    )

    train_df.to_parquet(TRAIN_PATH, index=False)
    valid_df.to_parquet(VALID_PATH, index=False)
    test_df.to_parquet(TEST_PATH, index=False)

    print("\nSplits Successfully Generated & Saved:")
    print(f"  Train Set      : {len(train_df):>10,} rows ({len(train_df)/total_samples:>6.1%}) | Fraud Ratio: {train_df['is_fraud'].mean():.4%} -> {TRAIN_PATH.name}")
    print(f"  Validation Set : {len(valid_df):>10,} rows ({len(valid_df)/total_samples:>6.1%}) | Fraud Ratio: {valid_df['is_fraud'].mean():.4%} -> {VALID_PATH.name}")
    print(f"  Test Set       : {len(test_df):>10,} rows ({len(test_df)/total_samples:>6.1%}) | Fraud Ratio: {test_df['is_fraud'].mean():.4%} -> {TEST_PATH.name}")
    print("=" * 70)


def main():
    full_path = generate_full_dataset()
    create_train_valid_test_splits(full_path)


if __name__ == "__main__":
    main()
