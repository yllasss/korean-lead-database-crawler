import pandas as pd
from pathlib import Path

def emergency_run():
    print("🚨 Bypassing SQL... Scanning raw files for 2024 and 2025...")
    
    def get_data(year):
        path = Path(f'./{year}')
        all_data = []
        # Find any file that looks like an Income Statement (PL)
        for f in path.rglob("*.txt"):
            if "Consolidated" in f.name and ("_PL_" in f.parent.name or "Income" in f.parent.name):
                try:
                    # Read with high-tolerance encoding
                    temp_df = pd.read_csv(f, sep='\t', encoding='cp949')
                    temp_df['year'] = year
                    all_data.append(temp_df)
                except Exception as e:
                    print(f"  Warning: skipped {f.name} ({e})")
                    continue
        return pd.concat(all_data) if all_data else pd.DataFrame()

    df25 = get_data('2025')
    df24 = get_data('2024')

    if df25.empty or df24.empty:
        print(f"❌ Data missing in folders. 2025 count: {len(df25)}, 2024 count: {len(df24)}")
        return

    # THE MAGIC FIX: Use 'Stock code' if 'corp_code' is missing
    # Every public company has a 6-digit stock code (e.g., 005930)
    def clean_df(df):
        df = df.copy()
        # Clean the stock code to ensure it's a 6-digit string
        if 'Stock code' in df.columns:
            df['ID'] = df['Stock code'].astype(str).str.strip().str.zfill(6)
        else:
            # Fallback to a very aggressive name clean
            df['ID'] = df['Company name'].astype(str).str.replace(r'[^a-zA-Z0-9]', '', regex=True).str.upper()
        
        df['val'] = pd.to_numeric(df['Current term'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        return df

    c25 = clean_df(df25)
    c24 = clean_df(df24)

    # Pivot to get Revenue and R&D
    def pivot_metrics(df):
        rev = df[df['Element name'].str.contains('Revenue|매출액', case=False, na=False)]
        rnd = df[df['Element name'].str.contains('Research|Development|연구개발', case=False, na=False)]
        
        r_sum = rev.groupby(['ID', 'Company name'])['val'].sum().reset_index(name='Rev')
        rd_sum = rnd.groupby('ID')['val'].sum().reset_index(name='RnD')
        return pd.merge(r_sum, rd_sum, on='ID', how='left').fillna(0)

    m25 = pivot_metrics(c25)
    m24 = pivot_metrics(c24)

    # JOIN ON THE ID (Stock Code)
    final = pd.merge(m25, m24, on='ID', suffixes=('_25', '_24'))
    
    print(f"🎯 SUCCESS: Matched {len(final)} companies via Stock Code!")
    
    if not final.empty:
        final['RnD_Growth'] = ((final['RnD_25'] - final['RnD_24']) / final['RnD_24'].replace(0,1)) * 100
        print(final[['Company name_25', 'Rev_25', 'RnD_Growth']].sort_values('RnD_Growth', ascending=False).head(10))
        final.to_csv('emergency_momentum.csv', index=False)

if __name__ == "__main__":
    emergency_run()