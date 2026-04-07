import sqlite3
import pandas as pd

conn = sqlite3.connect('market_research.db')

# 1. Check which years are actually present
print("--- Available Years in PL Table ---")
print(pd.read_sql("SELECT DISTINCT year_folder FROM PL", conn))

# 2. Check a few company names from each year to see if they match format
print("\n--- 2025 Sample Names ---")
print(pd.read_sql("SELECT DISTINCT \"Company name\" FROM PL WHERE year_folder = '2025' LIMIT 5", conn))

print("\n--- 2024 Sample Names ---")
print(pd.read_sql("SELECT DISTINCT \"Company name\" FROM PL WHERE year_folder = '2024' LIMIT 5", conn))

conn.close()