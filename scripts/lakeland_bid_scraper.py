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
OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL') # if using Abacus AI drop-in replacement
PORTAL_URL = "https://procurement.opengov.com/portal/lakelandgov"

if not DATABASE_URL or not OPENAI_API_KEY:
    print("❌ FATAL: Missing database or OpenAI/Abacus credentials.")
    sys.exit(1)

# Initialize OpenAI client (can point to Abacus AI proxy if OPENAI_BASE_URL is set)
client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL if OPENAI_BASE_URL else None
)

async def scrape_opengov_portal():
    print("🚀 Launching Playwright to scrape OpenGov portal...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to the portal and wait for network to settle so SPA hydrates
        await page.goto(PORTAL_URL, wait_until='networkidle')
        await asyncio.sleep(5) # buffer for internal react renders
        
        # We extract the entire innerText so the LLM has all the semantic context without HTML noise
        raw_text = await page.evaluate("document.body.innerText")
        await browser.close()
        
        if len(raw_text) < 500:
            print("❌ Error: Extracted text is too short. SPA might not have hydrated.")
            return None
            
        print(f"✅ Scraping complete. Extracted {len(raw_text)} characters of raw portal text.")
        return raw_text

async def parse_bids_with_llm(raw_text):
    print("🧠 Passing raw text to GPT-4o for structured intelligence extraction...")
    
    prompt = """
    You are an expert Government Contracting Data Analyst. 
    Below is the raw text scraped from the City of Lakeland's OpenGov procurement portal.
    Your job is to identify all ACTIVE Request for Proposals (RFPs), Bids, or RFQs.
    
    Extract them into a strict JSON array of objects with the following keys:
    - "title": The name of the project.
    - "closing_date": The deadline/closing date (format as YYYY-MM-DD if possible, else just the string).
    - "estimated_budget": The budget if mentioned, otherwise "Unknown".
    - "required_certs": Any specific certifications mentioned, else "Unknown".
    - "category": Categorize the project into one of these strict buckets: 
      ['Plumber', 'HVAC', 'Roofer', 'Electrician', 'Landscaper', 'Pest Control', 'Cleaning', 'General Contractor', 'Painter', 'Mover', 'Other']
    - "scope_summary": A 1-2 sentence compelling summary of what the city needs.
    
    Return ONLY valid JSON. Do not include markdown formatting block quotes like ```json.
    
    RAW TEXT:
    """ + raw_text[:30000] # Safe limit for token context

    response = await client.chat.completions.create(
        model="gpt-4o-mini", # Standardizing on fast, cheap, high-context models
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
            
        bids = json.loads(json_output)
        print(f"✅ LLM successfully extracted {len(bids)} structured bids.")
        return bids
    except Exception as e:
        print("❌ Error parsing LLM JSON response:", e)
        print("Raw output:", response.choices[0].message.content)
        return []

def inject_bids_to_neon(bids):
    if not bids:
        print("⚠️ No bids to inject.")
        return

    print("💾 Connecting to Neon Postgres to inject Bids...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    inserted_count = 0
    for bid in bids:
        # Check if bid already exists to prevent duplicate cron inserts
        cur.execute("SELECT id FROM bids WHERE title = %s", (bid.get('title'),))
        if cur.fetchone():
            print(f"⏩ Skipping existing bid: {bid.get('title')[:30]}...")
            continue
            
        cur.execute("""
            INSERT INTO bids (title, closing_date, estimated_budget, required_certs, category, scope_summary)
            VALUES (%s, null, %s, %s, %s, %s)
            RETURNING id;
        """, (
            bid.get('title'),
            bid.get('estimated_budget'),
            bid.get('required_certs'),
            bid.get('category'),
            bid.get('scope_summary')
        ))
        
        inserted_id = cur.fetchone()[0]
        inserted_count += 1
        print(f"✅ Inserted Bid ID {inserted_id}: {bid.get('title')[:30]}...")

    conn.commit()
    cur.close()
    conn.close()
    print(f"🎉 Database injection complete. Added {inserted_count} new RFPs.")

async def main():
    print("="*50)
    print("🚀 SOVEREIGN RFP SCRAPER DAEMON INITIATING")
    print("="*50)
    
    raw_text = await scrape_opengov_portal()
    if not raw_text:
        return
        
    structured_bids = await parse_bids_with_llm(raw_text)
    inject_bids_to_neon(structured_bids)
    print("✅ Nightly Daemon execution cycle complete.")

if __name__ == "__main__":
    asyncio.run(main())
