    import joblib
    import pandas as pd
    import numpy as np
    from pathlib import Path

    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    RANDOM_STATE = 42

    #project paths 

    BASE_DIR = Path(__file__).resolve().parent.parent 

    RAW_DATA_PATH = (
        BASE_DIR
        / "data"
        / "raw"
        / "financial_fraud_detection_dataset.csv"
    )

    PROCESSED_DIR = BASE_DIR / "data" / "processed"

    MODEL_DIR = (
        BASE_DIR
        / "models"
        / "saved_models"
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    #COLUMNS
    TARGET_COLUMN = "is_fraud"

    DROP_COLUMNS = [
        "transaction_id",
        "sender_account",
        "receiver_account",
        "ip_address",
        "device_hash",
        "fraud_type",
    ]

    CATEGORICAL_COLUMNS = [
        "transaction_type",
        "merchant_category",
        "location",
        "device_used",
        "payment_channel",
    ]

    NUMERICAL_COLUMNS = [
        "amount",
        "time_since_last_transaction",
        "spending_deviation_score",
        "velocity_score",
        "geo_anomaly_score",
        "hour",
        "day_of_week",
        "month",
        "is_weekend",
        "is_first_transaction",
    ]

    #LOAD DATASET 

    def load_dataset() -> pd.DataFrame:

        print("=" * 60)
        print("Loading Dataset...")
        print("=" * 60)
        print(f"Dataset Path : {RAW_DATA_PATH}")

        df = pd.read_csv(RAW_DATA_PATH)

        print(f"Dataset Shape : {df.shape}")

        return df

    #DROP DATASET 
    def drop_unused_columns(df: pd.DataFrame) -> pd.DataFrame:

        print("\nDropping unused columns...")

        df = df.drop(columns=DROP_COLUMNS)

        print(f"Remaining Columns : {len(df.columns)}")

        return df

    #TIME FEATURE ENGINEERING 
    def create_time_features(df: pd.DataFrame) -> pd.DataFrame:

        print("\nCreating time features...")

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            format="mixed",
            errors="coerce",
        )

        df["hour"] = df["timestamp"].dt.hour

        df["day_of_week"] = df["timestamp"].dt.dayofweek

        df["month"] = df["timestamp"].dt.month

        df["is_weekend"] = (
            df["day_of_week"] >= 5
        ).astype(int)

        df = df.drop(columns=["timestamp"])

        return df

    #MISSING VALUE HANDELING
    def handle_missing_values(
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        print("\nHandling missing values...")

        df["is_first_transaction"] = (
            df["time_since_last_transaction"]
            .isna()
            .astype(int)
        )

        df["time_since_last_transaction"] = (
            df["time_since_last_transaction"]
            .fillna(-1)
        )

        return df

    # ==========================================================
    # Split Features and Target
    # ==========================================================

    def split_features_target(
        df: pd.DataFrame,
    ):

        print("\nSplitting Features and Target...")

        X = df.drop(columns=[TARGET_COLUMN])

        y = df[TARGET_COLUMN]

        print(f"Feature Shape : {X.shape}")
        print(f"Target Shape  : {y.shape}")

        return X, y


    # ==========================================================
    # Build Preprocessing Pipeline
    # ==========================================================

    def build_preprocessor():

        print("\nBuilding preprocessing pipeline...")

        numeric_transformer = Pipeline(
            steps=[
                ("scaler", StandardScaler())
            ]
        )

        categorical_transformer = Pipeline(
            steps=[
                (
                    "encoder",
                    OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False,
                    ),
                )
            ]
        )

        preprocessor = ColumnTransformer(
            transformers=[
                (
                    "numerical",
                    numeric_transformer,
                    NUMERICAL_COLUMNS,
                ),
                (
                    "categorical",
                    categorical_transformer,
                    CATEGORICAL_COLUMNS,
                ),
            ]
        )

        return preprocessor

    # ==========================================================
    # Train Test Split
    # ==========================================================

    def split_train_test(
        X,
        y,
    ):

        print("\nSplitting Train/Test...")

        return train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=RANDOM_STATE,
            stratify=y,
        )

    # ==========================================================
    # Fit and Transform Data
    # ==========================================================

    def fit_preprocessor(
        preprocessor,
        X_train,
        X_test,
    ):

        print("\nFitting preprocessing pipeline...")

        X_train_processed = preprocessor.fit_transform(X_train)

        X_test_processed = preprocessor.transform(X_test)

        print(f"Processed Train Shape : {X_train_processed.shape}")
        print(f"Processed Test Shape  : {X_test_processed.shape}")

        return (
            X_train_processed,
            X_test_processed,
            preprocessor,
        )

    # ==========================================================
    # Save Processed Data
    # ==========================================================

    def save_artifacts(
        X_train,
        X_test,
        y_train,
        y_test,
        preprocessor,
    ):

        print("\nSaving processed datasets...")

        joblib.dump(
            X_train,
            PROCESSED_DIR / "X_train.pkl",
        )

        joblib.dump(
            X_test,
            PROCESSED_DIR / "X_test.pkl",
        )

        joblib.dump(
            y_train,
            PROCESSED_DIR / "y_train.pkl",
        )

        joblib.dump(
            y_test,
            PROCESSED_DIR / "y_test.pkl",
        )

        joblib.dump(
            preprocessor,
            MODEL_DIR / "preprocessor.pkl",
        )

        print("Saved successfully.")    


    def main() -> None:

        df = load_dataset()

        df = drop_unused_columns(df)

        df = create_time_features(df)

        df = handle_missing_values(df)

        X, y = split_features_target(df)

        preprocessor = build_preprocessor()

        X_train, X_test, y_train, y_test = split_train_test(
            X,
            y,
        )

        X_train_processed, X_test_processed, preprocessor = fit_preprocessor(
            preprocessor,
            X_train,
            X_test,
        )

        save_artifacts(
            X_train_processed,
            X_test_processed,
            y_train,
            y_test,
            preprocessor,
        )

        print("\nPreprocessing completed successfully.")


    if __name__ == "__main__":
        main()