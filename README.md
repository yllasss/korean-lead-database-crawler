# DART Financial Parser — AI Readiness Pipeline

A fault-tolerant ETL pipeline that transforms raw Korean DART filings into a ranked list of enterprise targets for AI adoption outreach. Built for real-world data conditions: inconsistent encoding, schema drift, and mismatched company identifiers across filing years.

---

## Architecture

```
Raw DART .txt files
        │
        ▼
ingest_and_clean.py       ← encoding fallback, statement classification, deduplication
        │
        ▼
   SQLite DB (market_research.db)
   ┌─────┬─────┬─────┬─────┐
   │ BS  │ PL  │ CF  │ CE  │
   └──┬──┴──┬──┴─────┴─────┘
      │     │
      ▼     ▼
┌─────────────────────────────────────┐
│         Three execution paths        │
│                                     │
│  1. account_list.py   (SQL pivot)   │
│  2. emergency.py      (file scan)   │
│  3. nuclear_pipeline.py (dict join) │
└──────────────┬──────────────────────┘
               │
               ▼
     final_target_list.py
               │
               ▼
   MCKINSEY_MASTER_TARGETS.csv
```

Rather than a single pipeline, the system provides three execution paths that degrade gracefully as data quality worsens. Run whichever path succeeds given your data.

---

## File Reference

| File | Role |
|---|---|
| `ingest_and_clean.py` | Ingests raw `.txt` filings, classifies by statement type, normalizes numerics, saves to `cleaned_output/` |
| `load_to_sql.py` | Loads cleaned CSVs into SQLite; also serves as a DB diagnostic tool |
| `account_list.py` | **Primary path** — SQL pivot to compute R&D intensity and operating margin for 2025 |
| `sql_analysis.py` | Diagnostic: checks year coverage and sample company names in the DB |
| `deep.py` | Diagnostic: prints raw company name strings per year to inspect formatting inconsistencies |
| `emergency.py` | **Fallback path** — bypasses SQL entirely; scans raw `.txt` files and joins on stock code |
| `nuclear_pipeline.py` | **Recovery path** — dictionary-based match after aggressive name normalization; no joins |
| `final_target_list.py` | Merges momentum data from `emergency.py` with 2025 BS liquidity; produces final scored list |

---

## Scoring Logic

The final priority score combines two percentile ranks:

| Signal | Weight | Rationale |
|---|---|---|
| R&D growth (YoY, capped at 500%) | 50% | Active innovation investment |
| Liquidity ratio (current assets / current liabilities) | 50% | Capacity to fund transformation |

Revenue scale is used as a filter (`Rev_25 > 1e10`), not a scoring input. This is intentional — revenue growth alone was not predictive of AI readiness in initial analysis.

---

## Usage

### Step 1 — Ingest raw filings

```bash
python ingest_and_clean.py
```

Expects DART `.txt` files under `./2024/` and `./2025/`. Only processes consolidated statements (`Consolidated` in filename). Outputs to `cleaned_output/master_BS.csv`, `master_PL.csv`, etc.

### Step 2 — Load to SQLite

```bash
python load_to_sql.py
```

Loads the cleaned CSVs into `market_research.db`. Run again at any time to inspect table structure and row counts.

### Step 3 — Run analysis (choose path based on data quality)

```bash
# Primary path: fast SQL pivot — works when schema is clean
python account_list.py

# Fallback path: file scan + stock code join — use if SQL pivot fails
python emergency.py

# Recovery path: dictionary-based match after nuclear name cleaning — last resort
python nuclear_pipeline.py
```

### Step 4 — Generate final target list

```bash
python final_target_list.py
```

Requires `emergency_momentum.csv` from `emergency.py`. Adds liquidity data from 2025 balance sheets and outputs `MCKINSEY_MASTER_TARGETS.csv`.

---

## Diagnostics

If company name matching fails between years, run the diagnostic scripts before escalating to a fallback path:

```bash
python sql_analysis.py   # check year coverage and name samples in DB
python deep.py           # print raw name strings to spot encoding/format issues
```

---

## Outputs

| File | Source | Contents |
|---|---|---|
| `account_list.csv` | `account_list.py` | R&D intensity + operating margin, 2025 |
| `emergency_momentum.csv` | `emergency.py` | YoY R&D growth via stock code join |
| `nuclear_momentum_list.csv` | `nuclear_pipeline.py` | Scored list from dictionary match |
| `MCKINSEY_MASTER_TARGETS.csv` | `final_target_list.py` | Final ranked targets with priority score |

---

## Data Notes

- **Encoding**: filings may be UTF-8 or CP949 (Korean EUC-KR/Windows-949). All loaders attempt UTF-8 first and fall back to CP949.
- **Company identity**: DART filings do not always use consistent company names across years. The fallback paths use 6-digit stock codes as the stable join key. The nuclear path uses aggressive string normalization (`[^A-Z0-9가-힣]` stripped, uppercased) as a last resort.
- **Bilingual labels**: metric extraction uses both Korean and English element name patterns (e.g. `매출액|Revenue`, `연구개발|Research`).
- **Consolidated only**: `ingest_and_clean.py` skips non-consolidated filings to avoid double-counting subsidiary data.

---

## Requirements

```
pandas
sqlite3   # stdlib
pathlib   # stdlib
```

---

## Roadmap

- Extend ingestion to Japan FSA and Singapore MAS filings
- Build a unified cross-country schema for regional comparisons
- Add visualization layer for scoring and segment analysis
