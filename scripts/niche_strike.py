
import os
import requests
import json
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GOOGLE_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def niche_strike(niche="restaurant", city="Lakeland FL"):
    print(f"🎯 NICHE STRIKE: {niche} in {city}...")
    
    # 1. Discover via Google
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": f"{niche} in {city}", "key": GOOGLE_KEY}
    
    try:
        r = requests.get(url, params=params)
        results = r.json().get("results", [])
        print(f"  Found {len(results)} total businesses.")
        
        # 2. Filter for "New/Neglected" (Reviews < 10)
        target_leads = [b for b in results if b.get("user_ratings_total", 0) < 10]
        print(f"  🎯 High-Intent Targets (Reviews < 10): {len(target_leads)}")
        
        for lead in target_leads:
            biz_name = lead.get("name")
            rating = lead.get("rating", 0)
            reviews = lead.get("user_ratings_total", 0)
            
            # Check duplicate
            dup = requests.get(f"{SUPABASE_URL}/rest/v1/contacts_master?company_name=eq.{biz_name}", headers=HEADERS)
            if dup.status_code == 200 and dup.json():
                print(f"  ⏩ Skipping duplicate: {biz_name}")
                continue
                
            # Insert as 'new' to trigger enrichment strike
            print(f"  ✅ Targeting: {biz_name} ({rating}⭐, {reviews} reviews)")
            requests.post(f"{SUPABASE_URL}/rest/v1/contacts_master", headers=HEADERS, json={
                "company_name": biz_name,
                "full_name": "Business Owner",
                "phone": lead.get("formatted_phone_number", ""),
                "website_url": "", # Will be enriched
                "status": "new",
                "lead_source": "niche_strike",
                "niche": niche,
                "raw_research": json.dumps({
                    "google_rating": rating,
                    "google_reviews": reviews,
                    "target_reason": "Low Visibility / New Business"
                })
            })
            
    except Exception as e:
        print(f"  ❌ Strike error: {e}")

if __name__ == "__main__":
    niche_strike("landscaping", "Lakeland FL")
    niche_strike("hvac", "Lakeland FL")
    niche_strike("pest control", "Lakeland FL")
