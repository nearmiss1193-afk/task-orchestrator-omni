"""
Prospecting Worker - Scrapes Google Maps for businesses without websites
Runs every 6 hours via Railway Cron
"""
import os
import re
import time
import json
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import shared clients
from supabase_client import get_client, insert_lead

# Configuration
SEARCH_QUERIES = [
    "HVAC contractor Lakeland FL",
    "roofing company Polk County FL",
    "plumber Lakeland Florida",
    "electrician Winter Haven FL",
    "landscaping company Lakeland FL"
]

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")


def scrape_google_maps_basic(query: str, limit: int = 20) -> list:
    """
    Basic Google Places API search for businesses.
    Returns businesses with missing/weak websites.
    """
    if not GOOGLE_PLACES_API_KEY:
        print("⚠️ GOOGLE_PLACES_API_KEY not set, using mock data")
        return get_mock_leads(query)
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": GOOGLE_PLACES_API_KEY
    }
    
    leads = []
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            for place in data.get("results", [])[:limit]:
                # Get place details for website
                details = get_place_details(place["place_id"])
                
                # Only interested in businesses without websites or with weak presence
                website = details.get("website", "")
                
                lead = {
                    "business_name": place.get("name", ""),
                    "location": place.get("formatted_address", ""),
                    "phone": details.get("formatted_phone_number", ""),
                    "website_url": website,
                    "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}",
                    "industry": extract_industry(query),
                    "status": "new",
                    "source": "google_maps_scrape",
                    "scraped_at": datetime.utcnow().isoformat()
                }
                
                # Flag if no website (hot prospect)
                if not website:
                    lead["fit_score"] = 80  # High priority - no website
                else:
                    lead["fit_score"] = 50  # Has website, need to audit
                
                leads.append(lead)
                
    except Exception as e:
        print(f"❌ Google Places API error: {e}")
    
    return leads


def get_place_details(place_id: str) -> dict:
    """Get detailed info for a place"""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website,opening_hours,rating,user_ratings_total",
        "key": GOOGLE_PLACES_API_KEY
    }
    
    try:
        with httpx.Client(timeout=15) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json().get("result", {})
    except:
        return {}


def extract_industry(query: str) -> str:
    """Extract industry from search query"""
    industries = {
        "hvac": "HVAC",
        "roofing": "Roofing",
        "plumb": "Plumbing",
        "electric": "Electrical",
        "landscap": "Landscaping",
        "lawn": "Lawn Care",
        "clean": "Cleaning",
        "paint": "Painting",
        "pool": "Pool Service"
    }
    
    query_lower = query.lower()
    for key, value in industries.items():
        if key in query_lower:
            return value
    return "General Contractor"


def get_mock_leads(query: str) -> list:
    """Return mock leads for testing when API key not available"""
    return [
        {
            "business_name": f"Test {extract_industry(query)} Company 1",
            "location": "Lakeland, FL 33801",
            "phone": "863-555-0101",
            "website_url": "",  # No website = hot prospect
            "industry": extract_industry(query),
            "status": "new",
            "fit_score": 80,
            "source": "mock_data"
        },
        {
            "business_name": f"Test {extract_industry(query)} Company 2",
            "location": "Winter Haven, FL 33880",
            "phone": "863-555-0102",
            "website_url": "http://example-slow-site.com",
            "industry": extract_industry(query),
            "status": "new",
            "fit_score": 50,
            "source": "mock_data"
        }
    ]


def deduplicate_leads(leads: list) -> list:
    """Remove duplicates based on phone or business name"""
    seen_phones = set()
    seen_names = set()
    unique = []
    
    for lead in leads:
        phone = lead.get("phone", "").replace("-", "").replace(" ", "")
        name = lead.get("business_name", "").lower().strip()
        
        if phone and phone not in seen_phones:
            seen_phones.add(phone)
            seen_names.add(name)
            unique.append(lead)
        elif not phone and name and name not in seen_names:
            seen_names.add(name)
            unique.append(lead)
    
    return unique


def check_existing_lead(phone: str, business_name: str) -> bool:
    """Check if lead already exists in database"""
    client = get_client()
    
    # Check by phone first
    if phone:
        clean_phone = phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        result = client.table("contacts_master") \
            .select("id") \
            .ilike("phone", f"%{clean_phone[-10:]}%") \
            .limit(1) \
            .execute()
        if result.data:
            return True
    
    # Check by business name
    if business_name:
        result = client.table("contacts_master") \
            .select("id") \
            .ilike("business_name", f"%{business_name}%") \
            .limit(1) \
            .execute()
        if result.data:
            return True
    
    return False


def run_prospecting_cycle():
    """Main prospecting cycle - run this every 6 hours"""
    print(f"\n{'='*60}")
    print(f"🔍 PROSPECTING WORKER - {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    all_leads = []
    
    for query in SEARCH_QUERIES:
        print(f"📍 Searching: {query}")
        leads = scrape_google_maps_basic(query, limit=20)
        print(f"   Found {len(leads)} leads")
        all_leads.extend(leads)
        time.sleep(2)  # Rate limiting
    
    # Deduplicate
    unique_leads = deduplicate_leads(all_leads)
    print(f"\n📊 Total unique leads: {len(unique_leads)}")
    
    # Insert new leads
    inserted = 0
    skipped = 0
    
    for lead in unique_leads:
        if check_existing_lead(lead.get("phone", ""), lead.get("business_name", "")):
            skipped += 1
            continue
        
        try:
            insert_lead(lead)
            inserted += 1
            print(f"   ✅ Inserted: {lead['business_name']}")
        except Exception as e:
            print(f"   ❌ Error inserting {lead['business_name']}: {e}")
    
    print(f"\n📈 RESULTS:")
    print(f"   Inserted: {inserted}")
    print(f"   Skipped (duplicates): {skipped}")
    print(f"   Total in this run: {len(unique_leads)}")
    
    return {"inserted": inserted, "skipped": skipped}


if __name__ == "__main__":
    run_prospecting_cycle()
