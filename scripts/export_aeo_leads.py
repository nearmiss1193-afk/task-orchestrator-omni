import os
import requests
import csv
import json
from datetime import datetime
from dotenv import load_dotenv

# Load credentials
load_dotenv()
load_dotenv('.env.local')

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not SUPABASE_KEY:
    print("❌ ERROR: Set SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY in .env")
    exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "count=exact"
}

def export_aeo_prospects():
    """Extract AEO prospects: targeted industries, low ratings or no website."""
    print("🚀 EXPORT: Fetching Lakeland leads for AEO Campaign...")
    
    all_leads = []
    offset = 0
    batch = 1000
    
    target_industries = ["pool", "lawn", "hvac", "plumbing", "roofing", "restaurant", "auto", "mechanic", "dental", "dentist", "medical", "real estate", "property"]
    
    while True:
        url = f"{SUPABASE_URL}/rest/v1/contacts_master"
        params = {
            "select": "*",
            "offset": offset,
            "limit": batch,
            "order": "created_at.desc"
        }
        
        resp = requests.get(url, headers=HEADERS, params=params)
        if resp.status_code != 200:
            print(f"ERROR: {resp.status_code} - {resp.text}")
            break
            
        data = resp.json()
        if not data:
            break
            
        for lead in data:
            biz_name = (lead.get("company_name", "") or "")
            industry = (lead.get("vertical", "") or "")
            
            # Check AEO vulnerability: No website OR rating < 4.5 OR reviews < 20
            has_website = bool(lead.get("website_url"))
            rating = lead.get("google_rating") or 5.0
            reviews = lead.get("google_reviews") or 0
            
            if not has_website or rating < 4.5 or reviews < 20:
                # Compile for export
                all_leads.append({
                    "id": lead.get("id"),
                    "business_name": biz_name,
                    "phone": lead.get("phone", ""),
                    "website": lead.get("website_url", ""),
                    "rating": rating,
                    "review_count": reviews,
                    "industry": industry,
                    "vulnerability": "No Website" if not has_website else f"Low Rating/Reviews ({rating} stars / {reviews} reviews)",
                })
                
            if len(all_leads) >= 250:
                break
        
        print(f"  Processed batch... Found {len(all_leads)} AEO prospects so far.")
        if len(all_leads) >= 250:
            break
        offset += batch
        if len(data) < batch:
            break

    os.makedirs("exports", exist_ok=True)
    filename = f"exports/aeo_prospects_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["id", "business_name", "phone", "website", "rating", "review_count", "industry", "vulnerability"])
        writer.writeheader()
        writer.writerows(all_leads)
        
    print(f"✅ EXPORT COMPLETE: {len(all_leads)} prime AEO prospects saved to {filename}")

if __name__ == "__main__":
    export_aeo_prospects()
