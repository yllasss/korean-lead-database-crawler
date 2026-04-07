import pandas as pd
import sqlite3

conn = sqlite3.connect('market_research.db')

try:
    # 1. Load the PL and BS data
    print("Fetching and processing financial data...")
    df_pl = pd.read_sql("SELECT * FROM PL WHERE year_folder = '2025'", conn)
    df_bs = pd.read_sql("SELECT * FROM BS WHERE year_folder = '2025'", conn)
finally:
    conn.close()

def clean_and_pivot(df):
    # Convert 'Current term' to numeric, removing commas if they exist
    df['Current term'] = pd.to_numeric(df['Current term'].astype(str).str.replace(',', ''), errors='coerce')
    # Pivot so each 'Element name' is a column for the company
    return df.pivot_table(index=['Company name', 'Industry name'], 
                         columns='Element name', 
                         values='Current term', 
                         aggfunc='sum').reset_index()

pl_wide = clean_and_pivot(df_pl)
bs_wide = clean_and_pivot(df_bs)

# 2. Merge PL and BS data
target_list = pd.merge(pl_wide, bs_wide, on='Company name', suffixes=('', '_BS'))

# 3. Calculate McKinsey Strategic Metrics
# Note: These column names should be adjusted based on your 'Element name' output
# We use .filter to find relevant columns even if the exact naming varies
target_list['Revenue'] = target_list.filter(like='Revenue').sum(axis=1) + target_list.filter(like='매출액').sum(axis=1)
target_list['RnD'] = target_list.filter(like='Research').sum(axis=1) + target_list.filter(like='연구개발').sum(axis=1)
target_list['Op_Income'] = target_list.filter(like='Operating income').sum(axis=1) + target_list.filter(like='영업이익').sum(axis=1)

# --- THE INSIGHTS ---
# A. R&D Intensity: Who is investing in the future?
target_list['RnD_Intensity'] = (target_list['RnD'] / target_list['Revenue']) * 100

# B. Efficiency: Who has low margins and needs optimization?
target_list['Op_Margin'] = (target_list['Op_Income'] / target_list['Revenue']) * 100

# 4. Create the final prioritized list
# We filter for companies with Revenue > 0 to avoid division errors
final_list = target_list[target_list['Revenue'] > 0].sort_values(by='RnD_Intensity', ascending=False)

# Select and rename for clarity
output = final_list[['Company name', 'Industry name_BS', 'Revenue', 'RnD_Intensity', 'Op_Margin']]
output.columns = ['Company', 'Industry', 'Total_Revenue', 'RnD_Intensity_%', 'Operating_Margin_%']

print("\nTOP 10 STRATEGIC TARGETS (High R&D Intensity):")
print(output.head(10))

# Save for your workflow
output.to_csv('account_list.csv', index=False)