import pandas as pd
import sqlite3
from pathlib import Path

from ingestion_db import ingest_df
from logger_setup import get_logger

logger = get_logger("vendor_summary")


def create_vendor_summary(conn):
    """Merge tables and create vendor summary."""

    try:
        logger.info("Creating vendor summary table...")

        sql_path = Path("SQL_QUERY/vendor_summary.sql")

        with open(sql_path, 'r', encoding='utf-8') as file:
            query = file.read()

        vendor_sales_summary = pd.read_sql_query(query, conn)

        logger.info(
            f"Vendor summary created successfully. Shape: {vendor_sales_summary.shape}"
        )

        return vendor_sales_summary

    except FileNotFoundError:
        logger.exception("SQL file not found.")
        raise

    except Exception:
        logger.exception("Error while creating vendor summary.")
        raise


def clean_data(df):
    """Clean the dataframe."""

    try:
        logger.info("Cleaning data...")

        # Change datatype
        df['Volume'] = df['Volume'].astype('float64')

        # Handle missing values
        df.fillna(0, inplace=True)

        # Remove extra spaces
        df['VendorName'] = df['VendorName'].str.strip()
        df['Description'] = df['Description'].str.strip()

        logger.info("Data cleaned successfully.")

        return df

    except KeyError:
        logger.exception("Required columns missing during cleaning.")
        raise

    except Exception:
        logger.exception("Unexpected error during cleaning.")
        raise


def add_calculated_columns(df):
    """Add calculated columns."""

    try:
        logger.info("Adding calculated columns...")

        required_cols = [
            'TotalSalesDollars',
            'TotalPurchaseDollars',
            'TotalSalesQuantity',
            'TotalPurchaseQuantity'
        ]

        missing_cols = [
            col for col in required_cols
            if col not in df.columns
        ]

        if missing_cols:
            raise KeyError(
                f"Missing columns: {missing_cols}"
            )

        df['GrossProfit'] = (
            df['TotalSalesDollars']
            - df['TotalPurchaseDollars']
        )

        df['ProfitMargin'] = (
            df['GrossProfit']
            / df['TotalSalesDollars']
        ) * 100

        df['StockTurnover'] = (
            df['TotalSalesQuantity']
            / df['TotalPurchaseQuantity']
        )

        df['SalesToPurchaseRatio'] = (
            df['TotalSalesDollars']
            / df['TotalPurchaseDollars']
        )

        logger.info("Calculated columns added successfully.")

        return df

    except Exception:
        logger.exception(
            "Error while adding calculated columns."
        )
        raise


if __name__ == "__main__":

    conn = None

    try:
        conn = sqlite3.connect("inventory.db")

        logger.info("Connected to database.")
        print("Connected successfully.")

        summary_df = create_vendor_summary(conn)

        cleaned_df = clean_data(summary_df)

        final_df = add_calculated_columns(cleaned_df)

        logger.info(
            f"Final dataframe shape: {final_df.shape}"
        )

        ingest_df(
            final_df,
            'vendor_sales_summary',
            conn,
            mode='replace'
        )

        logger.info("Data saved successfully.")
        print("Data saved successfully.")

    except Exception:
        logger.exception(
            "Pipeline execution failed."
        )
        print("Pipeline failed. Check logs.")

    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")