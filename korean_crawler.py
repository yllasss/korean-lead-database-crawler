import asyncio
import re
from crawlee.basic_crawler import BasicCrawler
from bs4 import BeautifulSoup
import csv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Korean companies to crawl
KOREAN_COMPANIES = {
    'KB Kookmin Bank': 'https://www.kbfingroup.com',
    'Shinhan Bank': 'https://www.shinhan.com',
    'Woori Bank': 'https://www.wooribank.com',
    'Samsung Electronics': 'https://www.samsung.com',
    'LG Electronics': 'https://www.lg.com',
    'Naver': 'https://www.naver.com',
    'Kakao': 'https://www.kakao.com',
    'Coupang': 'https://www.coupang.com',
    'SK Telecom': 'https://www.sktelecom.com',
    'KT Corporation': 'https://www.kt.com',
}

results = []

def extract_employees(text):
    """Find employee count in text"""
    match = re.search(r'([\d,]+)\s*(?:\+)?\s*employees', text, re.IGNORECASE)
    if match:
        return match.group(1).replace(',', '')
    
    match = re.search(r'([\d,]+)\s*명(?:의)?\s*직원', text)
    if match:
        return match.group(1).replace(',', '')
    
    return None

def extract_revenue(text):
    """Find revenue in text"""
    match = re.search(r'\$\s*([\d.]+)\s*(billion|million)', text, re.IGNORECASE)
    if match:
        return match.group(0)
    return None

async def crawl_company(company_name, website_url):
    """Crawl one company"""
    print(f"\nCrawling: {company_name}")
    
    crawler = BasicCrawler(
        max_requests_per_crawl=5,
        max_crawl_depth=1,
        headless=True,
    )
    
    company_data = {
        'company_name': company_name,
        'website': website_url,
        'employees': None,
        'revenue': None,
    }
    
    async def handler(context):
        try:
            page = context.page
            body = await page.content()
            soup = BeautifulSoup(body, 'html.parser')
            
            for script in soup(['script', 'style']):
                script.decompose()
            
            text = soup.get_text()
            
            employees = extract_employees(text)
            if employees and not company_data['employees']:
                company_data['employees'] = employees
                print(f"  ✓ Found {employees:,} employees")
            
            revenue = extract_revenue(text)
            if revenue and not company_data['revenue']:
                company_data['revenue'] = revenue
                print(f"  ✓ Found revenue: {revenue}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    urls = [
        website_url,
        f"{website_url}/about",
        f"{website_url}/about-us",
        f"{website_url}/company",
        f"{website_url}/careers",
    ]
    
    urls = list(set([u.rstrip('/') for u in urls if u]))
    
    crawler.add_requests(urls)
    crawler.add_page_handler(handler)
    
    try:
        await crawler.run()
    except Exception as e:
        print(f"  Crawler error: {e}")
    
    results.append(company_data)
    print(f"✓ Done: {company_name}")
    
    await asyncio.sleep(1)

async def main():
    print("\n" + "="*50)
    print("KOREAN COMPANY CRAWLER")
    print("="*50)
    
    for company_name, website in KOREAN_COMPANIES.items():
        await crawl_company(company_name, website)
    
    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['company_name', 'website', 'employees', 'revenue'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n{'='*50}")
    print(f"✓ Done! Saved to results.csv")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    asyncio.run(main())