import logging
from datetime import datetime
from typing import Optional

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from telegram_llm_chatbot.db.database import get_enginge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to export table data to CSV
def export_table_to_df(table_name: str, start_date: Optional[datetime] = None) -> pd.DataFrame:
    load_dotenv(find_dotenv(usecwd=True))

    # Establish a connection to the PostgreSQL database using the get_enginge function
    engine = get_enginge()

    df = pd.DataFrame()
    query = f"SELECT * FROM {table_name}"
    if start_date:
        query += f" WHERE timestamp >= '{start_date}'"

    try:
        df = pd.read_sql_query(query, engine)
    except Exception as e:
        logger.warning(f"Error exporting data from table {table_name}: {e}")
        df = pd.DataFrame()

    return df
