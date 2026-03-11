import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'finance.db')
DB_URL = f"sqlite:///{DB_PATH}"

def get_engine():
    return create_engine(DB_URL)

def run_query(sql: str) -> pd.DataFrame:
    """Execute a SQL query and return results as a DataFrame."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            df = pd.read_sql_query(text(sql), conn)
        return df
    except Exception as e:
        raise ValueError(f"SQL execution error: {str(e)}")

def get_schema() -> str:
    """Return full schema as a string for the LLM to read."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    schema_parts = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()

        cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
        sample_rows = cursor.fetchall()

        col_defs = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
        sample_str = "\n  ".join([str(row) for row in sample_rows])
        schema_parts.append(
            f"Table: {table}\n"
            f"  Columns: {col_defs}\n"
            f"  Sample rows:\n  {sample_str}"
        )

    conn.close()
    return "\n\n".join(schema_parts)