import pandas as pd

from preprocessing.feature_pipeline import (
    FeaturePipeline,
)

df = pd.read_csv(
    "data/raw/HI-Small_Trans.csv",
    nrows=20,
)

pipeline = FeaturePipeline()

features = pipeline.process_dataframe(
    df,
)

print(features.head(20))

print()

print(features.columns.tolist())