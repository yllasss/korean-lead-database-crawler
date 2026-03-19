# 🇰🇷 Korean Corporate Intelligence Pipeline (v2.0)

A high-performance data pipeline designed to extract official headcount and revenue metrics for 450+ Korean enterprises and Upstage MOU partners.

## 🚀 The Evolution: Scraping vs. API
This project transitioned from a **Playwright-based web scraper** to an **OpenDART API pipeline**.

| Feature | Scraper (v1.0) | OpenDART API (v2.0) |
| :--- | :--- | :--- |
| **Accuracy** | Estimated (Regex) | **Official / Audited** |
| **Success Rate** | ~7% (due to 404s/Redirects) | **~98% (Listed Companies)** |
| **Speed** | 60s/company (DOM Load) | **<1s/company (JSON)** |
| **Stability** | Fragile (UI Changes) | **Robust (Versioned API)** |

## 🛠️ Architecture
The pipeline uses a **Hybrid Strategy**:
1. **Primary (OpenDART):** Fetches audited financial data for KOSPI/KOSDAQ listed entities using unique 8-digit Corp Codes.
2. **Fallback (Async Scraper):** Best-effort extraction for private startups and foreign partners (e.g., Coupang, FuriosaAI) using `aiohttp` and `BeautifulSoup`.

## ⚙️ Installation & Setup

1. **Clone & Environment:**
   ```bash
   git clone [https://github.com/your-username/korean-lead-crawler.git](https://github.com/your-username/korean-lead-crawler.git)
   cd korean-lead-crawler
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt

2. **API Authentication::**
   Register at OpenDART and add your key to a .env file:
Plaintext
DART_API_KEY=your_40_character_key_here


📊 Data Coverage
Employee Metrics: Total headcount from empSttus.json (Annual Reports).

Financial Metrics: Revenue (매출액/영업수익) converted to 억원 (100M KRW units).

Timeframe: Automated fallback logic checks 2025 → 2024 → 2023 filings to ensure the most recent data is captured.

🛡️ Ethics & Compliance
Rate Limiting: Implements asyncio.Semaphore to stay within the 100 req/min DART threshold.

User-Agent: Identifies as a research crawler to remain transparent to webmasters.
