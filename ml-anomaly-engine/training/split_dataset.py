from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET = (
    BASE_DIR
    / "data"
    / "processed"
    / "training_dataset_hi_li_small.parquet"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

RANDOM_STATE = 42


def main():

    df = pd.read_parquet(DATASET)

    train, temp = train_test_split(
        df,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=df["is_fraud"],
    )

    valid, test = train_test_split(
        temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=temp["is_fraud"],
    )

    train.to_parquet(
        OUTPUT_DIR / "train.parquet",
        index=False,
    )

    valid.to_parquet(
        OUTPUT_DIR / "valid.parquet",
        index=False,
    )


    test.to_parquet(
        OUTPUT_DIR / "test.parquet",
        index=False,
    )

    print("Train:", train.shape)
    print("Validation:", valid.shape)
    print("Test:", test.shape)


if __name__ == "__main__":
    main()