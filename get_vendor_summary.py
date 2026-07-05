import pandas as pd
import sqlite3
import logging
import os
from ingestion_db import ingest_df
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "get_vendor_summary.log"

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',filemode='a')

def create_vendor_summary(conn):

    ''' this function will merge the diffrent tables and create a vendor summary table by adding new columns and save it to the database'''
    
    logging.info('Creating vendor summary table by merging the different tables and adding new columns.')
    sql_path = Path("SQL_QUERY/vendor_summary.sql")
    
    with open(sql_path, 'r', encoding='utf-8') as file:
        query = file.read()

    vendor_sales_summary = pd.read_sql_query(query, conn)
    logging.info('Vendor summary table created successfully.')
    return vendor_sales_summary

def clean_data(df):
    ''' this function will clean the data by changing data types and handling missing values'''
    logging.info('Cleaning the data...')

    # changing data types
    df['Volume'] = df['Volume'].astype('float64')

    # Handle missing values
    df.fillna(0, inplace=True)

    # removing unnecessary spaces from catagorical columns
    df['VendorName'] = df['VendorName'].str.strip()
    df['Description'] = df['Description'].str.strip()
    logging.info('Data cleaned successfully.')
    return df

def add_calculated_columns(df):
    ''' this function will add calculated columns to the dataframe'''
    logging.info('Adding calculated columns...')
    # adding new columns
    df['GrossProfit'] = (df['TotalSalesDollars'] - df['TotalPurchaseDollars']) 
    df['ProfitMargin'] = (df['GrossProfit'] / df['TotalSalesDollars']) * 100
    df['StockTurnover'] = df['TotalSalesQuantity'] / df['TotalPurchaseQuantity']
    df['SalesToPurchaseRatio'] = df['TotalSalesDollars'] / df['TotalPurchaseDollars']
    logging.info('Calculated columns added successfully.')

    return df


if __name__ == "__main__":

    conn = sqlite3.connect('inventory.db')
    logging.info('Connected to the database successfully.')
    print('Connected to the database successfully.')

    summary_df = create_vendor_summary(conn)
    logging.info(summary_df.head())
    print('Vendor summary table created successfully.')

    cleaned_data = clean_data(summary_df)

    final_data = add_calculated_columns(cleaned_data)
    logging.info(final_data.head())
    print('Final data prepared successfully.')

    logging.info('Final data prepared successfully and started saving to the database.')
    ingest_df(final_data,'vendor_sales_summary', conn,mode='replace')
    logging.info('Final data saved to the database successfully.')
    print('Final data saved to the database successfully.')