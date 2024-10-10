import os
import datetime
import pandas as pd
import psycopg2
from dotenv import find_dotenv, load_dotenv


# Function to export table data to CSV
def export_table_to_df(table_name: str, start_date: datetime.datetime = None) -> pd.DataFrame:
    
    load_dotenv(find_dotenv(usecwd=True))

    # Retrieve environment variables
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")


    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    if not start_date:
        query = f"SELECT * FROM {table_name}"
    else:
        try:
            query = f"SELECT * FROM {table_name} WHERE timestamp >= '{start_date}'"
            df = pd.read_sql_query(query, conn)
        except:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(query, conn)
    conn.close()
    return df
