import pandas as pd
from pathlib import Path

def generate_final_targets():
    print("🚀 Finalizing Master List...")
    
    # 1. Load the successful momentum data
    try:
        mom_df = pd.read_csv('emergency_momentum.csv')
        mom_df['ID'] = mom_df['ID'].astype(str).str.zfill(6)
    except FileNotFoundError:
        print("❌ Run emergency.py first!")
        return

    # 2. Scrape 2025 BS folders directly for Liquidity
    print("🔍 Extracting Liquidity from 2025 Balance Sheets...")
    bs_data = []
    path_2025 = Path('./2025')
    
    for f in path_2025.rglob("*.txt"):
        # Look for Consolidated Balance Sheets
        if "Consolidated" in f.name and ("_BS_" in f.parent.name or "Position" in f.parent.name):
            try:
                temp_df = pd.read_csv(f, sep='\t', encoding='cp949')
                # Identify Stock code column dynamically
                s_col = [c for c in temp_df.columns if 'Stock' in c or 'code' in c.lower()]
                if s_col:
                    temp_df['ID'] = temp_df[s_col[0]].astype(str).str.strip().str.zfill(6)
                    bs_data.append(temp_df)
            except Exception as e:
                print(f"  Warning: skipped {f.name} ({e})")
                continue

    if not bs_data:
        print("❌ Could not find 2025 BS files in folders.")
        return

    df_bs = pd.concat(bs_data)
    
    # 3. Calculate Liquidity Ratio
    def clean_val(col):
        return pd.to_numeric(col.astype(str).str.replace(',', ''), errors='coerce').fillna(0)

    df_bs['val'] = clean_val(df_bs['Current term'])
    
    # Pivot to get Assets vs Liabilities
    bs_pivot = df_bs.pivot_table(index='ID', columns='Element name', values='val', aggfunc='sum')
    
    # Standard DART labels for Liquidity
    assets = bs_pivot.filter(like='Current assets').sum(axis=1)
    liabilities = bs_pivot.filter(like='Current liabilities').sum(axis=1)
    bs_pivot['Liquidity_Ratio'] = (assets / liabilities.replace(0, 1)).round(2)

    # 4. Final Merge
    final = pd.merge(mom_df, bs_pivot[['Liquidity_Ratio']], on='ID', how='left').fillna(1.0)

    # 5. Clean Outliers and Score
    # We cap RnD_Growth at 500% to keep the ranking realistic
    final['RnD_Growth_Capped'] = final['RnD_Growth'].clip(upper=500)
    
    # Priority Score (0-10)
    final['Priority_Score'] = (
        (final['RnD_Growth_Capped'].rank(pct=True) * 5) + 
        (final['Liquidity_Ratio'].rank(pct=True) * 5)
    ).round(1)

    # 6. Output the Golden List
    report = final[final['Rev_25'] > 1e10].sort_values('Priority_Score', ascending=False)
    
    print("\n🎯 TOP 10 STRATEGIC ACCOUNTS (Ranked by Momentum & Liquidity):")
    cols = ['Company name_25', 'Rev_25', 'RnD_Growth', 'Liquidity_Ratio', 'Priority_Score']
    print(report[cols].head(10).to_string(index=False))

    report.to_csv('ai_readiness_targets.csv', index=False)
    print(f"\n✅ Created target list with {len(report)} qualified accounts.")

if __name__ == "__main__":
    generate_final_targets()