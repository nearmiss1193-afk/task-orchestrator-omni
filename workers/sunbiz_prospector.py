"""
SUNBIZ LAKELAND PROSPECTOR v1
=============================
Scrapes search.sunbiz.org for businesses in Lakeland, FL.
Extracts Mailing Address and Principal names for FDBR Strike targeting.
"""
import os
import re
import time
import json
import requests
from datetime import datetime, timezone

def scrape_sunbiz_lakeland(city="Lakeland"):
    """
    Search Sunbiz by City and extract results.
    Note: Sunbiz is notoriously difficult to scrape. This uses a simple search approach.
    """
    url = "https://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults"
    params = {
        "SearchType": "EntityName",
        "SearchTerm": city,
        "SearchDirection": "Next"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    leads = []
    try:
        r = requests.get(url, params=params, headers=headers, timeout=30)
        if r.status_code != 200:
            print(f"❌ Sunbiz error: {r.status_code}")
            return []
            
        # Extract Entity Names and Document Numbers using Regex (for speed/portability)
        # Search results typically have <td class="small-width"><a href="...">ENTITY NAME</a></td>
        pattern = r"href=\"(/Inquiry/CorporationSearch/SearchResultDetail/.*?)\">(.*?)</a>"
        matches = re.findall(pattern, r.text)
        
        for link, name in matches[:20]: # Limit for safety
            if city.upper() in name.upper():
                leads.append({
                    "business_name": name.strip(),
                    "source_url": f"https://search.sunbiz.org{link}",
                    "source": "sunbiz_lakeland",
                    "status": "new"
                })
        
        print(f"✅ Sunbiz: Found {len(leads)} potential leads for {city}")
        return leads
    except Exception as e:
        print(f"❌ Sunbiz failure: {e}")
        return []

def run_sunbiz_sync():
    """Main sync loop into Supabase"""
    from modules.database.supabase_client import get_supabase
    supabase = get_supabase()
    
    leads = scrape_sunbiz_lakeland()
    count = 0
    for lead in leads:
        # Dedupe by name
        res = supabase.table("contacts_master").select("id").ilike("company_name", lead["business_name"]).execute()
        if not res.data:
            supabase.table("contacts_master").insert({
                "company_name": lead["business_name"],
                "status": "new",
                "source": "sunbiz",
                "niche": "Local Business",
                "raw_research": json.dumps({"source": "sunbiz", "scraped_at": datetime.now(timezone.utc).isoformat()})
            }).execute()
            count += 1
            print(f"  📥 Inserted: {lead['business_name']}")
            
    return count

if __name__ == "__main__":
    run_sunbiz_sync()
