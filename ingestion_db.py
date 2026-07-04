import pandas as pd
from sqlalchemy import create_engine
import os
import time

from pathlib import Path
import logging

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "data_ingestion.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

engine = create_engine('sqlite:///inventory.db')

def ingest_df(df,table_name,engine,mode):
    '''This function ingests a DataFrame into the database table.'''
    df.to_sql(table_name, con=engine, if_exists=mode, index=False)

def load_raw_data():
    '''This function loads all CSV files from the 'data' directory into the database in chunks.'''
    start_time = time.time()
    
    # 1. Define a safe chunk size (e.g., 50,000 rows at a time)
    CHUNK_SIZE = 50000 
    
    for file in os.listdir('data'):
        if file.endswith('.csv'):
            file_path = os.path.join('data', file)
            table_name = file.split('.')[0]
            logging.info(f'----Starting ingestion for {file}----')
            
            #  Read the CSV in chunks using TextFileReader iterator
            chunks = pd.read_csv(file_path, chunksize=CHUNK_SIZE)
            
            for i, chunk_df in enumerate(chunks):

                logging.info(f'Ingesting chunk {i+1} of {file} into table {table_name}')
                
                #  Call ingestion function per chunk
                mode = "replace" if i == 0 else "append"
                ingest_df(chunk_df, table_name, engine,mode)
                
                del chunk_df
                import gc; gc.collect()
                
    end_time = time.time()
    logging.info('----Ingestion completed----')
    logging.info(f'Total time taken for ingestion: {end_time - start_time:.2f} seconds')

if __name__ == "__main__":
    load_raw_data()