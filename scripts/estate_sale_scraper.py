import os
import sys
import json
import asyncio
import psycopg2
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from openai import AsyncOpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 1. Configuration
DATABASE_URL = os.environ.get('NEON_DATABASE_URL') or os.environ.get('DATABASE_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or os.environ.get('ABACUS_API_KEY')
OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL') 
PORTAL_URL = "https://www.estatesales.net/FL/Lakeland" # Target vector

if not DATABASE_URL or not OPENAI_API_KEY:
    print("❌ FATAL: Missing database or OpenAI/Abacus credentials.")
    sys.exit(1)

# Initialize OpenAI client 
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL if OPENAI_BASE_URL else None
)

async def scrape_estate_sales():
    print("🚀 Launching Playwright to scrape EstateSales.net (Lakeland Vector)...")
    async with async_playwright() as p:
        # Using a mobile user-agent to bypass some basic anti-bot logic if necessary
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()
        
        await page.goto(PORTAL_URL, wait_until='networkidle')
        await asyncio.sleep(5) 
        
        # Scroll to load lazy images/text
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
        await asyncio.sleep(2)
        
        raw_text = await page.evaluate("document.body.innerText")
        await browser.close()
        
        if len(raw_text) < 500:
            print("❌ Error: Extracted text is too short. Potential bot block.")
            return None
            
        print(f"✅ Scraping complete. Extracted {len(raw_text)} characters of raw portal text.")
        return raw_text

async def parse_intent_with_llm(raw_text):
    print("🧠 Passing raw text to GPT-4o-mini for Intent Classification...")
    
    prompt = """
    You are an expert Lead Generation Analyst. 
    Below is the raw text scraped from an Estate Sales and Yard Sales aggregator for Lakeland, Florida.
    Your job is to identify all upcoming distinct sales. DO NOT hallucinate. Only extract what is clearly a sale listing.
    
    Extract them into a strict JSON array of objects with the following keys:
    - "title": The name or headline of the sale.
    - "event_date": The date(s) the sale is occurring.
    - "address": The physical location of the sale (or 'Address released later' if obscured).
    - "sale_type": Categorize strictly as one of: ['Estate Sale', 'Moving Sale', 'Yard Sale', 'Warehouse Liquidation', 'Other']. 
    - "intent_classification": Categorize the likely underlying event driving the sale. Choose strictly from: ['Moving/Relocating', 'Estate Clearing/Probate', 'Spring Cleaning', 'Business Liquidation', 'Unknown'].
    - "description_summary": A 1-2 sentence compelling summary of the items listed. Focus heavily on if it mentions tools, appliances, or "entire house" vs just clothes/knick-knacks.
    
    Return ONLY valid JSON. Do not include markdown formatting block quotes like ```json.
    
    RAW TEXT:
    """ + raw_text[:30000] 

    response = await client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": "You output only valid JSON arrays."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    try:
        json_output = response.choices[0].message.content.strip()
        if json_output.startswith("```json"):
            json_output = json_output[7:-3]
            
        sales = json.loads(json_output)
        print(f"✅ LLM successfully extracted {len(sales)} structured sales events.")
        return sales
    except Exception as e:
        print("❌ Error parsing LLM JSON response:", e)
        print("Raw output:", response.choices[0].message.content)
        return []

def inject_sales_to_neon(sales):
    if not sales:
        print("⚠️ No sales to inject.")
        return

    print("💾 Connecting to Neon Postgres to inject Intent Data...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    inserted_count = 0
    for sale in sales:
        # We use a loose uniqueness check based on title and date to prevent dupes
        cur.execute("SELECT id FROM estate_sales WHERE title = %s AND event_date = %s", (sale.get('title'), sale.get('event_date')))
        if cur.fetchone():
            print(f"⏩ Skipping existing sale: {sale.get('title')[:30]}...")
            continue
            
        cur.execute("""
            INSERT INTO estate_sales (title, event_date, address, url, sale_type, intent_classification, description_summary)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            sale.get('title'),
            sale.get('event_date'),
            sale.get('address'),
            PORTAL_URL, # Base URL reference
            sale.get('sale_type'),
            sale.get('intent_classification'),
            sale.get('description_summary')
        ))
        
        inserted_id = cur.fetchone()[0]
        inserted_count += 1
        print(f"✅ Inserted Intent ID {inserted_id}: {sale.get('title')[:30]} [{sale.get('intent_classification')}]")

    conn.commit()
    cur.close()
    conn.close()
    print(f"🎉 Database injection complete. Added {inserted_count} new physical events.")

async def main():
    print("="*50)
    print("🚀 SOVEREIGN INTENT ENGINE DAEMON INITIATING")
    print("="*50)
    
    raw_text = await scrape_estate_sales()
    if not raw_text:
        return
        
    structured_sales = await parse_intent_with_llm(raw_text)
    inject_sales_to_neon(structured_sales)
    print("✅ Nightly Daemon execution cycle complete.")

if __name__ == "__main__":
    asyncio.run(main())
