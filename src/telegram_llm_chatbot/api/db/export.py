import os

import pandas as pd
import psycopg2
from dotenv import find_dotenv, load_dotenv


# Function to export table data to CSV
def export_table_to_df(table_name: str) -> pd.DataFrame:
    
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


    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df
