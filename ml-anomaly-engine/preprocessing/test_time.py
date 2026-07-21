import pandas as pd

from preprocessing.feature_engineering import (
    extract_time_features,
    compute_velocity_score,
    compute_time_since_last_transaction,
)

df = pd.read_csv(
    "data/raw/HI-Small_Trans.csv",
    nrows=100,
)

df = extract_time_features(df)

df = compute_velocity_score(df)

df = compute_time_since_last_transaction(df)

df = compute_spending_deviation(df)

print(
    df[
        [
            "Account",
            "Amount Paid",
            "velocity_score",
            "time_since_last_transaction",
            "spending_deviation_score",
        ]
    ].head(30)
)
