import os
import json
import time
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv

# Import functions from prospector
# We need to add workers to sys.path
import sys
sys.path.append(os.getcwd())

from workers.prospector import (
    discover_businesses, 
    enrich_with_email, 
    calculate_lead_score, 
    is_duplicate, 
    insert_lead,
    NICHES,
    CITIES,
    CITY_REGIONS
)
from modules.database.supabase_client import get_supabase

load_dotenv()

def run_targeted_offensive():
    print(f"\n{'='*60}")
    print(f"🎯 LAKELAND 'BLEEDING LEADS' OFFENSIVE STARTING 🎯")
    print(f"{'='*60}")

    supabase = get_supabase()
    google_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_PLACES_API_KEY")
    hunter_key = os.environ.get("HUNTER_API_KEY", "")

    if not google_key:
        print("❌ Error: Missing Google API Key")
        return

    # TIER 1 VERTICALS ONLY
    TARGET_NICHES = [
        "tree removal", "gutter installation", "pool service", 
        "lawn care", "hvac", "plumbing", "roofing"
    ]
    
    # LAKELAND CORE ONLY
    LAKELAND_CITIES = [
        "Lakeland FL", "33801", "33803", "33805", "33809", "33810",
        "33811", "33812", "33813", "33815"
    ]

    total_inserted = 0
    
    for city in LAKELAND_CITIES:
        for niche in TARGET_NICHES:
            query = f"{niche} {city}"
            print(f"\n🔎 Searching Lakeland: {query}")
            
            raw_leads = discover_businesses(query, google_key)
            print(f"  Found {len(raw_leads)} potential businesses.")
            
            for lead_data in raw_leads:
                biz_name = lead_data.get("business_name", "")
                
                # Enrichment
                lead = enrich_with_email(lead_data, hunter_key)
                
                # Score
                lead["score"] = calculate_lead_score(lead)
                
                # Check for contact info
                if not lead.get("email") and not lead.get("phone"):
                    continue
                
                # Dedup
                if is_duplicate(supabase, lead.get("phone", ""), biz_name, lead.get("email", "")):
                    continue
                
                # Insert
                if insert_lead(supabase, lead, niche, city):
                    total_inserted += 1
                    status = "📧" if lead.get("email") else "📞"
                    print(f"  ✅ {status} [{lead['score']}/10] {biz_name}")
                
                if total_inserted >= 20: # Limit for speed in this run
                    break
            
            if total_inserted >= 20:
                break
            time.sleep(2)
        
        if total_inserted >= 20:
            break

    print(f"\n✅ OFFENSIVE COMPLETE: {total_inserted} high-priority Lakeland leads added.")

if __name__ == "__main__":
    run_targeted_offensive()
