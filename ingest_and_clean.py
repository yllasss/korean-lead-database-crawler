import pandas as pd
from pathlib import Path

# --- CONFIGURATION ---
BASE_PATH = Path('.') 
OUTPUT_FOLDER = Path('cleaned_output')
OUTPUT_FOLDER.mkdir(exist_ok=True)

# Categorization buckets based on DART folder naming conventions
DATA_BUCKETS = {
    "BS": [], # Balance Sheet
    "PL": [], # Profit & Loss (Income Statement)
    "CF": [], # Cash Flow
    "CE": []  # Changes in Equity
}

def clean_financial_value(val):
    """Converts DART string '1,234,567' or empty to a proper integer."""
    if pd.isna(val) or str(val).strip() == '' or str(val).strip() == 'null':
        return 0
    try:
        # Remove commas and whitespace
        return int(str(val).replace(',', '').strip())
    except ValueError:
        return 0

print("🚀 Starting Batch Processing...")

# --- 1. CRAWL AND LOAD ---
for file_path in BASE_PATH.rglob("*.txt"):
    filename = file_path.name
    parent_folder = file_path.parent.name
    
    # Skip non-consolidated files to avoid duplicate company data
    # (Consolidated = '연결' or 'Consolidated' in the name)
    if "Consolidated" not in filename:
        continue

    # Identify which bucket this file belongs to
    statement_type = None
    for key in DATA_BUCKETS.keys():
        if f"_{key}_" in parent_folder:
            statement_type = key
            break
    
    if not statement_type:
        continue

    # Attempt to load with Dual-Encoding Logic
    df = None
    try:
        df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
    except UnicodeDecodeError:
        try:
            # cp949 is the Python codec for Korean EUC-KR/Windows-949
            df = pd.read_csv(file_path, sep='\t', encoding='cp949')
        except Exception as e:
            print(f"❌ Permanent Failure: {filename} ({e})")
            continue

    # --- 2. DATA TRANSFORM ---
    if df is not None:
        # Add metadata so we know where/when the data is from
        df['year_folder'] = file_path.parts[0]
        df['source_file'] = filename
        df['statement_type'] = statement_type

        # Clean the numeric columns (DART usually provides Current, Previous, and Pre-Previous)
        # Note: Column names might vary slightly, but 'Current term' is the standard
        target_cols = ['Current term', 'Previous term']
        for col in target_cols:
            if col in df.columns:
                df[col] = df[col].apply(clean_financial_value)

        DATA_BUCKETS[statement_type].append(df)
        print(f"✅ Processed: {filename} -> {statement_type}")

# --- 3. MERGE AND SAVE ---
print("\nFinalizing Master Files...")
for st_type, df_list in DATA_BUCKETS.items():
    if df_list:
        # Combine all years/files for this type
        master_df = pd.concat(df_list, ignore_index=True)
        
        # Deduplicate: If the same company/account/year exists, keep the first one
        # This is vital for data integrity
        dedup_cols = ['Company name', 'Element name', 'year_folder']
        if all(c in master_df.columns for c in dedup_cols):
            before_count = len(master_df)
            master_df = master_df.drop_duplicates(subset=dedup_cols, keep='first')
            after_count = len(master_df)
            print(f"🧹 {st_type}: Removed {before_count - after_count} duplicate rows.")

        output_path = OUTPUT_FOLDER / f"master_{st_type}.csv"
        master_df.to_csv(output_path, index=False)
        print(f"💾 Saved {st_type} Master: {output_path} ({len(master_df)} rows)")

print("\n✨ All systems clear. Your clean data is in the 'cleaned_output' folder.")