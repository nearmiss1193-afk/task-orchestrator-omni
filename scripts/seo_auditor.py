import os
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from playwright.async_api import async_playwright

load_dotenv('C:/Users/nearm/.gemini/antigravity/scratch/empire-unified/.env')
db_url = os.environ.get('DATABASE_URL')
BASE_URL = "https://aiserviceco.com" # Assuming this is the production URL

async def audit_page(browser, slug):
    url = f"{BASE_URL}/{slug}"
    context = await browser.new_context()
    page = await context.new_page()
    
    result = {
        "url_slug": slug,
        "status_code": 0,
        "schema_present": False,
        "ai_content_verified": False,
        "fcp_ms": 0,
    }
    
    try:
        start_time = time.time()
        response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        end_time = time.time()
        
        result["status_code"] = response.status
        result["fcp_ms"] = int((end_time - start_time) * 1000)
        
        if response.status == 200:
            # Check for JSON-LD schema
            schema = await page.query_selector('script[type="application/ld+json"]')
            result["schema_present"] = schema is not None
            
            # Check for Market Analysis text (look for the header we added)
            # "Why [City] Needs AI for [Industry]"
            market_header = await page.query_selector('h2:has-text("Needs AI for")')
            result["ai_content_verified"] = market_header is not None
            
    except Exception as e:
        print(f"Error auditing {slug}: {e}")
        result["status_code"] = 500 # Assume server error or timeout
        
    await context.close()
    return result

async def run_auditor():
    if not db_url:
        print("❌ DATABASE_URL not found")
        return

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # 1. Fetch random batch of pages that haven't been checked recently or at all
    print("🔍 Fetching batch of pages for audit...")
    cur.execute("""
        SELECT s.slug 
        FROM seo_landing_pages s
        LEFT JOIN page_health_logs h ON s.slug = h.url_slug
        ORDER BY h.last_checked ASC NULLS FIRST
        LIMIT 20;
    """)
    rows = cur.fetchall()
    slugs = [row[0] for row in rows]
    
    if not slugs:
        print("✅ No pages found to audit.")
        return

    print(f"🕵️‍♂️ Starting audit for {len(slugs)} pages using Playwright...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for slug in slugs:
            print(f"  Checking /{slug}...")
            res = await audit_page(browser, slug)
            
            # 2. Upsert into page_health_logs
            cur.execute("""
                INSERT INTO page_health_logs (url_slug, status_code, schema_present, ai_content_verified, fcp_ms, last_checked)
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (url_slug) DO UPDATE SET
                    status_code = EXCLUDED.status_code,
                    schema_present = EXCLUDED.schema_present,
                    ai_content_verified = EXCLUDED.ai_content_verified,
                    fcp_ms = EXCLUDED.fcp_ms,
                    last_checked = NOW();
            """, (res["url_slug"], res["status_code"], res["schema_present"], res["ai_content_verified"], res["fcp_ms"]))
            conn.commit()
            
            status_icon = "✅" if res["status_code"] == 200 and res["schema_present"] and res["ai_content_verified"] else "❌"
            print(f"    {status_icon} Result: HTTP {res['status_code']} | Schema: {res['schema_present']} | AI: {res['ai_content_verified']}")

        await browser.close()
    
    cur.close()
    conn.close()
    print("🎉 Audit batch complete.")

if __name__ == "__main__":
    asyncio.run(run_auditor())
