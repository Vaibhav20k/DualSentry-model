from pathlib import Path
import time

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from preprocessing.feature_pipeline import (
    FeaturePipeline,
)

INPUT_FILES = [
    "HI-Small_Trans.csv",
    "LI-Small_Trans.csv",
]

OUTPUT_FILE = Path(
    "data/processed/training_dataset_hi_li_small.parquet"
)

CHUNK_SIZE = 250_000


def build_dataset():

    pipeline = FeaturePipeline()

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    writer = None

    total_rows = 0

    start = time.time()

    try:

        for input_file in INPUT_FILES:

            print()
            print("=" * 60)
            print(f"Processing {input_file}")
            print("=" * 60)

            input_path = (
                Path("data/raw")
                / input_file
            )

            for chunk in pd.read_csv(
                input_path,
                chunksize=CHUNK_SIZE,
            ):

                processed = pipeline.process_dataframe(
                    chunk,
                )

                table = pa.Table.from_pandas(
                    processed,
                    preserve_index=False,
                )

                if writer is None:

                    writer = pq.ParquetWriter(
                        OUTPUT_FILE,
                        table.schema,
                    )

                writer.write_table(
                    table,
                )

                total_rows += len(processed)

                print(
                    f"{input_file} | "
                    f"Chunk: {len(processed):,} | "
                    f"Total: {total_rows:,}"
                )

    finally:

        if writer is not None:

            writer.close()

    elapsed = time.time() - start

    print()
    print("=" * 60)
    print("Dataset Generated Successfully")
    print("=" * 60)

    print(
        f"Rows Processed : {total_rows:,}"
    )

    print(
        f"Output File    : {OUTPUT_FILE}"
    )

    print(
        f"Time Taken     : {elapsed / 60:.2f} minutes"
    )

    print("=" * 60)


if __name__ == "__main__":

    build_dataset()