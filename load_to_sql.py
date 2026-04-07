import sqlite3
import pandas as pd

db_name = 'market_research.db'

conn = None
try:
    conn = sqlite3.connect(db_name)
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)

    if tables.empty:
        print(f"Warning: database '{db_name}' is empty (no tables found).")
    else:
        print(f"--- Database summary: {db_name} ---")
        for table in tables['name']:
            count = pd.read_sql(f"SELECT COUNT(*) as total FROM {table}", conn).iloc[0]['total']
            print(f"Table: {table:<10} | Rows: {count}")
            peek = pd.read_sql(f"SELECT * FROM {table} LIMIT 1", conn)
            print(f"   Columns: {list(peek.columns)}\n")

except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    if conn:
        conn.close()