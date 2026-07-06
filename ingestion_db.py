import pandas as pd
from sqlalchemy import create_engine
import os
import time
import gc

from logger_setup import get_logger

logger = get_logger("data_ingestion")

engine = create_engine('sqlite:///inventory.db')


def ingest_df(df, table_name, engine, mode):
    """Ingest DataFrame into database table."""

    try:
        logger.info(f"Writing data to table '{table_name}' with mode='{mode}'")

        df.to_sql(table_name, con=engine, if_exists=mode, index=False)

        logger.info(f"Successfully wrote {len(df)} rows to '{table_name}'")

    except Exception:
        logger.exception(f"Failed while ingesting data into '{table_name}'")
        raise


def load_raw_data():
    """Load CSV files into database in chunks."""

    start_time = time.time()
    CHUNK_SIZE = 50000

    try:
        if not os.path.exists('data'):
            raise FileNotFoundError("Data directory not found.")

        csv_files = [file for file in os.listdir('data') if file.endswith('.csv')]

        if not csv_files:
            logger.warning("No CSV files found.")
            return

        for file in csv_files:
            file_path = os.path.join('data', file)
            table_name = file.split('.')[0]

            logger.info(f"----- Starting ingestion for {file} -----")

            try:
                chunks = pd.read_csv(file_path, chunksize=CHUNK_SIZE)

                for i, chunk_df in enumerate(chunks):
                    logger.info(
                        f"Ingesting chunk {i+1} ({len(chunk_df)} rows)"
                    )

                    mode = "replace" if i == 0 else "append"

                    ingest_df(chunk_df, table_name, engine, mode)

                    del chunk_df
                    gc.collect()

                logger.info(f"Completed ingestion for {file}")

            except Exception:
                logger.exception(f"Error processing file {file}")

        end_time = time.time()

        logger.info("----- Ingestion completed -----")
        logger.info(f"Total time: {end_time - start_time:.2f} sec")

    except Exception:
        logger.exception("Unexpected error during raw data loading")
        raise

    finally:
        engine.dispose()
        logger.info("Database resources released.")


if __name__ == "__main__":
    load_raw_data()