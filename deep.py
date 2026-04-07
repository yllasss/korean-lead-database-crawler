import sqlite3
import pandas as pd

conn = sqlite3.connect('market_research.db')
# Get 5 names from each year
n25 = pd.read_sql("SELECT DISTINCT \"Company name\" FROM PL WHERE year_folder = '2025' LIMIT 5", conn)
n24 = pd.read_sql("SELECT DISTINCT \"Company name\" FROM PL WHERE year_folder = '2024' LIMIT 5", conn)

print("2025 Names (Raw):", n25["Company name"].tolist())
print("2024 Names (Raw):", n24["Company name"].tolist())
conn.close()