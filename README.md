# Korean Lead Database Crawler

Web crawler for Korean companies to build lead database.

## Setup
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python korean_crawler.py
```

## What It Does

- Crawls 10+ Korean companies (banks, tech, telecom)
- Extracts employee count and revenue
- Exports to `results.csv`

## Companies

- KB Kookmin Bank
- Shinhan Bank
- Samsung Electronics
- Naver
- Kakao
- And more...

## Output

`results.csv` with:
- company_name
- website
- employees
- revenue