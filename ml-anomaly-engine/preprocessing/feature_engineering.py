from __future__ import annotations

import pandas as pd


def extract_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract temporal features from the IBM AML Timestamp column.

    Input:
        Timestamp

    Output:
        hour
        day_of_week
        month
        is_weekend
    """

    df = df.copy()

    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        errors="coerce",
    )

    df["hour"] = df["Timestamp"].dt.hour

    df["day_of_week"] = df["Timestamp"].dt.dayofweek

    df["month"] = df["Timestamp"].dt.month

    df["is_weekend"] = (
        df["day_of_week"] >= 5
    ).astype(int)

    return df

def compute_velocity_score(
    df: pd.DataFrame,
) -> pd.DataFrame:

    df = df.copy()

    df = df.sort_values(
        ["Account", "Timestamp"]
    )

    df["velocity_score"] = (
        df.groupby("Account")
        .cumcount()
        + 1
    )

    return df

def compute_time_since_last_transaction(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Computes elapsed seconds since the previous
    transaction of the same account.
    """

    df = df.copy()

    df = df.sort_values(
        ["Account", "Timestamp"]
    )

    df["time_since_last_transaction"] = (
        df.groupby("Account")["Timestamp"]
        .diff()
        .dt.total_seconds()
        .fillna(0)
    )

    return df

def compute_spending_deviation(
    df: pd.DataFrame,
) -> pd.DataFrame:

    df = df.copy()

    avg_amount = (
        df.groupby("Account")["Amount Paid"]
        .transform("mean")
    )

    std_amount = (
        df.groupby("Account")["Amount Paid"]
        .transform("std")
        .fillna(1)
    )

    df["spending_deviation_score"] = (
        (
            df["Amount Paid"] - avg_amount
        ) / std_amount
    ).fillna(0)

    return df