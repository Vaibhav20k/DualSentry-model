"""
create_chronological_split.py – generate deterministic chronological train/validation/test split.
"""

import pandas as pd
from pathlib import Path

# Directories
SCRIPT_DIR = Path(__file__).resolve().parent
DATASET_DIR = SCRIPT_DIR.parent
OUTPUTS_DIR = DATASET_DIR / "outputs"  # benchmark split location
CHRONO_DIR = DATASET_DIR / "chronological"
FULL_DATASET_PATH = OUTPUTS_DIR / "training_dataset_hi_li_small.parquet"

def create_chronological_split(full_path: Path, target_dir: Path, ratios=(0.70, 0.15, 0.15)) -> None:
    """Read full dataset, split chronologically, write parquet files.

    Parameters
    ----------
    full_path: Path
        Path to combined parquet file.
    target_dir: Path
        Destination directory for train/valid/test parquet files.
    ratios: tuple[float,float,float]
        Split proportions (train, valid, test).
    """
    df = pd.read_parquet(full_path)
    # Ensure strict chronological order (use original timestamp column if present)
    if "timestamp" in df.columns:
        df = df.sort_values("timestamp")
    else:
        # Fallback to hour/day ordering – should not happen in production
        df = df.sort_values(["hour", "day_of_week", "month"])
    total = len(df)
    train_end = int(total * ratios[0])
    valid_end = train_end + int(total * ratios[1])
    train_df = df.iloc[:train_end]
    valid_df = df.iloc[train_end:valid_end]
    test_df = df.iloc[valid_end:]
    target_dir.mkdir(parents=True, exist_ok=True)
    train_df.to_parquet(target_dir / "train.parquet", index=False)
    valid_df.to_parquet(target_dir / "valid.parquet", index=False)
    test_df.to_parquet(target_dir / "test.parquet", index=False)
    print(f"Chronological split written to {target_dir}")
    print(f"Rows – train: {len(train_df):,}, valid: {len(valid_df):,}, test: {len(test_df):,}")

if __name__ == "__main__":
    create_chronological_split(FULL_DATASET_PATH, CHRONO_DIR)
