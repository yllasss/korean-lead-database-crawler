# 🇰🇷 Korean Corporate Intelligence Pipeline (v3.0)

"""
DART Batch Filing Parser + Lead Scorer
=======================================
Reads the bulk TXT files from DART's batch download
(https://opendart.fss.or.kr/disclosureinfo/fnltt/dwld/main.do)
and extracts the four financial statements you downloaded:
 
  재무상태표   (Balance Sheet)      → Cash on Hand
  손익계산서   (Income Statement)   → Revenue, Net Profit, Growth
  현금흐름표   (Cash Flow)          → R&D spend, Operating CF
  자본변동표   (Changes in Equity)  → Dividends, Equity changes
 
HOW TO GET THE BATCH FILES:
  1. Go to https://opendart.fss.or.kr/disclosureinfo/fnltt/dwld/main.do
  2. Select: 사업보고서 (Annual Report) → 2024 and 2025
  3. Download each of the 4 statement ZIPs
  4. Unzip them into a folder, e.g.:
       ./dart_data/2024/BS/   (재무상태표)
       ./dart_data/2024/IS/   (손익계산서)
       ./dart_data/2024/CF/   (현금흐름표)
       ./dart_data/2024/CE/   (자본변동표)
       ./dart_data/2025/...   (same structure)
 
  Each file inside is a tab-separated TXT with columns:
    rcept_no, reprt_code, bsns_year, corp_code, sj_div,
    sj_nm, account_id, account_nm, account_detail,
    thstrm_nm, thstrm_amount, thstrm_add_amount,
    frmtrm_nm, frmtrm_amount, frmtrm_add_amount,
    bfefrmtrm_nm, bfefrmtrm_amount, bfefrmtrm_add_amount,
    ord, currency
 
HOW TO RUN:
  pip install pandas tqdm
  python dart_batch_parser.py
 
OUTPUT:
  master_leads_2026.csv   — every company with all extracted fields
  top_cash.csv            — ranked by cash on hand
  top_growth.csv          — ranked by YoY revenue growth
  top_rd.csv              — ranked by R&D investment
  summary.txt             — human-readable scout report
"""
 
