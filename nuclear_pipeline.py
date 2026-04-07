import pandas as pd
import sqlite3

def generate_momentum_nuclear():
    conn = sqlite3.connect('market_research.db')
    try:
        _run_nuclear(conn)
    finally:
        conn.close()

def _run_nuclear(conn):
    print("Running nuclear match (dictionary-based join)...")

    # 1. Load everything and force-clean company names
    df = pd.read_sql("SELECT * FROM PL", conn)
    df_bs = pd.read_sql("SELECT * FROM BS WHERE year_folder = '2025'", conn)
    
    # FORCE CLEANING
    df['Company name'] = df['Company name'].astype(str).str.strip().str.upper().str.replace(r'[^A-Z0-9가-힣]', '', regex=True)
    df['val'] = pd.to_numeric(df['Current term'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

    # 2. Extract Revenue & R&D manually to avoid Pivot failures
    # Revenue Search
    rev = df[df['Element name'].str.contains('Revenue|매출액|영업수익', case=False, na=False)]
    # R&D Search
    rnd = df[df['Element name'].str.contains('Research|Development|연구개발', case=False, na=False)]

    # 3. Create a Simple Dictionary-based Match
    # This is slower but 100% reliable compared to pd.merge
    def get_metrics(year):
        data = {}
        # Revenue
        y_rev = rev[rev['year_folder'] == year].groupby('Company name')['val'].sum()
        # R&D
        y_rnd = rnd[rnd['year_folder'] == year].groupby('Company name')['val'].sum()
        
        for name in y_rev.index:
            data[name] = {'Rev': y_rev[name], 'RnD': y_rnd.get(name, 0)}
        return data

    m25 = get_metrics('2025')
    m24 = get_metrics('2024')

    # 4. Find Overlap
    combined_list = []
    for name, vals in m25.items():
        if name in m24:
            row = {
                'Company': name,
                'Rev_25': vals['Rev'],
                'RnD_25': vals['RnD'],
                'Rev_24': m24[name]['Rev'],
                'RnD_24': m24[name]['RnD']
            }
            combined_list.append(row)

    final_df = pd.DataFrame(combined_list)
    print(f"✅ NUCLEAR MATCH SUCCESS: Found {len(final_df)} overlapping companies.")

    if final_df.empty:
        print("No overlapping names found even after nuclear cleaning.")
        print("Likely cause: 2024 and 2025 use completely different naming conventions.")
        return

    # 5. Add Liquidity from BS
    df_bs['Company name'] = df_bs['Company name'].astype(str).str.strip().str.upper().str.replace(r'[^A-Z0-9가-힣]', '', regex=True)
    df_bs['val'] = pd.to_numeric(df_bs['Current term'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    
    # Calculate Liquidity per company
    bs_agg = df_bs.pivot_table(index='Company name', columns='Element name', values='val', aggfunc='sum')
    liq = (bs_agg.filter(like='Current assets').sum(axis=1) / bs_agg.filter(like='Current liabilities').sum(axis=1).replace(0,1))
    
    final_df['Liquidity'] = final_df['Company'].map(liq).fillna(0)
    
    # 6. Final Scores
    final_df['RnD_Growth'] = ((final_df['RnD_25'] - final_df['RnD_24']) / final_df['RnD_24'].replace(0,1)) * 100
    final_df['Score'] = final_df['Rev_25'].rank(pct=True) + final_df['RnD_Growth'].rank(pct=True) + final_df['Liquidity'].rank(pct=True)

    report = final_df[final_df['Rev_25'] > 1e10].sort_values(by='Score', ascending=False)
    print("\n🏆 THE MCKINSEY TOP 10 (NUCLEAR MATCH):")
    print(report[['Company', 'Rev_25', 'RnD_Growth', 'Liquidity', 'Score']].head(10))
    
    report.to_csv('nuclear_momentum_list.csv', index=False)

if __name__ == "__main__":
    generate_momentum_nuclear()