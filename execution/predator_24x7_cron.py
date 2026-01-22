"""
24/7 PREDATOR PROSPECTOR - Modal Cron Job
Runs every 30 minutes to scrape new leads across all US time zones.
"""
import modal
import json
import os
from datetime import datetime
import requests

app = modal.App("predator-prospector-24x7")

image = modal.Image.debian_slim().pip_install(
    "playwright",
    "asyncio",
    "requests"
).run_commands("playwright install chromium")

@app.function(
    image=image,
    schedule=modal.Cron("*/30 * * * *"),  # Every 30 minutes
    timeout=600,
    secrets=[modal.Secret.from_name("agency-vault")]
)
async def prospect_loop():
    """
    24/7 Prospecting Loop - Runs every 30 minutes.
    Cycles through different cities and niches to ensure continuous lead flow.
    """
    from playwright.async_api import async_playwright
    
    # Rotate targets based on hour to cover all time zones
    hour = datetime.now().hour
    
    targets_by_shift = {
        "morning": [
            {"city": "New York", "niche": "personal injury lawyer"},
            {"city": "Miami", "niche": "water damage restoration"},
            {"city": "Atlanta", "niche": "hvac company"},
            {"city": "Charlotte", "niche": "roofing company"},
            {"city": "Boston", "niche": "seo agency"},
        ],
        "afternoon": [
            {"city": "Dallas", "niche": "personal injury lawyer"},
            {"city": "Houston", "niche": "emergency plumber"},
            {"city": "Chicago", "niche": "dui lawyer"},
            {"city": "Nashville", "niche": "cosmetic dentist"},
            {"city": "Denver", "niche": "solar company"},
        ],
        "evening": [
            {"city": "Los Angeles", "niche": "medspa"},
            {"city": "San Francisco", "niche": "personal injury lawyer"},
            {"city": "Seattle", "niche": "water damage restoration"},
            {"city": "Phoenix", "niche": "pool construction"},
            {"city": "Las Vegas", "niche": "estate lawyer"},
        ],
        "night": [
            {"city": "San Diego", "niche": "chiropractor"},
            {"city": "Portland", "niche": "landscaping design"},
            {"city": "Austin", "niche": "solar company"},
            {"city": "Tampa", "niche": "emergency plumber"},
            {"city": "Orlando", "niche": "hvac company"},
        ]
    }
    
    if 6 <= hour < 12:
        shift = "morning"
    elif 12 <= hour < 18:
        shift = "afternoon"
    elif 18 <= hour < 24:
        shift = "evening"
    else:
        shift = "night"
    
    targets = targets_by_shift[shift]
    all_leads = []
    
    print(f"🚀 PREDATOR 24/7 | Shift: {shift.upper()} | Targets: {len(targets)}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for target in targets:
            city = target["city"]
            niche = target["niche"]
            print(f"🕵️ Scanning: {niche} in {city}...")
            
            page = await browser.new_page()
            search_url = f"https://www.google.com/maps/search/{niche.replace(' ', '+')}+{city.replace(' ', '+')}"
            
            try:
                await page.goto(search_url, timeout=30000)
                await page.wait_for_timeout(5000)
                
                # Extract business cards from Maps
                results = await page.evaluate('''() => {
                    const cards = document.querySelectorAll('[data-result-index]');
                    return Array.from(cards).slice(0, 5).map(card => {
                        const name = card.querySelector('.fontHeadlineSmall')?.textContent || 'Unknown';
                        const rating = card.querySelector('.MW4etd')?.textContent || '0';
                        const website = card.querySelector('a[data-value="Website"]')?.href || '';
                        return { name, rating: parseFloat(rating) || 0, website };
                    });
                }''')
                
                for r in results:
                    r["city"] = city
                    r["niche"] = niche
                    r["scraped_at"] = datetime.now().isoformat()
                    all_leads.append(r)
                    print(f"✅ Found: {r['name']} ({r['rating']}⭐)")
                    
            except Exception as e:
                print(f"⚠️ Error in {city}: {str(e)}")
            finally:
                await page.close()
        
        await browser.close()
    
    print(f"\n🏆 Shift Complete: {len(all_leads)} leads captured.")
    
    # V2 MISSION: TRIGGER VORTEX ORCHESTRATOR
    webhook_url = "https://nearmiss1193-afk--v2-empire-fusion-orchestrate.modal.run"
    
    payload = {
        "campaign": "SMS_BLAST",
        "action": "start",
        "metadata": {
            "source": f"predator_24x7_{shift}",
            "batch_size": len(all_leads)
        },
        "leads": all_leads
    }
    
    try:
        print(f"📡 Uploading {len(all_leads)} leads to V2 Orchestrator...")
        res = requests.post(webhook_url, json=payload, timeout=30)
        if res.status_code == 200:
            print(f"✅ V2 UPLINK SUCCESS: {res.json().get('message')}")
            return {"status": "success", "leads": len(all_leads)}
        else:
            print(f"⚠️ V2 UPLINK FAIL: {res.status_code}")
            return {"status": "fail", "reason": res.text}
    except Exception as e:
        print(f"❌ V2 UPLINK ERROR: {str(e)}")
        return {"status": "error", "error": str(e)}

@app.local_entrypoint()
def main():
    """Test run locally"""
    import asyncio
    result = asyncio.run(prospect_loop.local())
    print(json.dumps(result, indent=2))
