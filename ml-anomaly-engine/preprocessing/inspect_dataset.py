import pandas as pd

df = pd.read_parquet(
    "data/processed/training_dataset.parquet"
)

print("=" * 60)
print("Shape")
print(df.shape)

print("\nColumns")
print(df.columns.tolist())

print("\nMissing Values")
print(df.isnull().sum())

print("\nFraud Distribution")
print(df["is_fraud"].value_counts())

print("\nFraud Percentage")
print(df["is_fraud"].value_counts(normalize=True) * 100)

print("\nSummary Statistics")
print(df.describe())