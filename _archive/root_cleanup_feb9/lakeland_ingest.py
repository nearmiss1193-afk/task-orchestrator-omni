
import os
import time
import requests
import json
from datetime import datetime
from modules.database.supabase_client import get_supabase

# MISSION: LAKELAND LOCAL INGESTION ENGINE
# Goal: 500-2,000 businesses across core categories.
# Isolation: Lives in its own script and targets a separate schema/ledger.

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

CATEGORIES = [
    "restaurant", "cafe", "plumber", "hvac", "electrician", 
    "beauty_salon", "gym", "dentist", "car_repair", "lodging"
]

LAKELAND_CENTER = "28.0395,-81.9498"
RADIUS = 15000 # 15km to cover Lakeland broadly

def ingest_businesses():
    supabase = get_supabase()
    if not supabase:
        print("❌ Ingestion Error: Supabase client init failed.")
        return

    print(f"🚀 LAKELAND INGESTION: Starting City-Scale Discovery...")
    
    total_new = 0
    
    for category in CATEGORIES:
        print(f"🔍 Scanning -> {category}...")
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": LAKELAND_CENTER,
            "radius": RADIUS,
            "type": category,
            "key": GOOGLE_API_KEY
        }
        
        try:
            while True:
                response = requests.get(url, params=params, timeout=15)
                data = response.json()
                results = data.get("results", [])
                
                for place in results:
                    place_id = place.get("place_id")
                    name = place.get("name")
                    
                    # Prepare for isolated storage
                    # For now, we use a separate table 'lakeland_directory'
                    entry = {
                        "place_id": place_id,
                        "name": name,
                        "category": category,
                        "address": place.get("vicinity"),
                        "latitude": place.get("geometry", {}).get("location", {}).get("lat"),
                        "longitude": place.get("geometry", {}).get("location", {}).get("lng"),
                        "rating": place.get("rating"),
                        "user_ratings_total": place.get("user_ratings_total"),
                        "raw_data": place,
                        "last_ingested_at": datetime.now().isoformat()
                    }
                    
                    # Deduplicated upsert
                    try:
                        # Attempt to insert into lakeland_directory
                        # Note: This table must exist or will be created/handled by Supabase
                        res = supabase.table("lakeland_directory").upsert(entry, on_conflict="place_id").execute()
                        if res.data:
                            total_new += 1
                    except Exception as db_err:
                        # If table doesn't exist, we log and skip
                        print(f"⚠️ [DMS] Skipping storage for {name} - lakeland_directory table potentially missing.")
                        break

                # Pagination
                next_page_token = data.get("next_page_token")
                if not next_page_token:
                    break
                
                # Google requires a short delay before the next_page_token becomes valid
                time.sleep(2)
                params = {
                    "pagetoken": next_page_token,
                    "key": GOOGLE_API_KEY
                }
                
        except Exception as e:
            print(f"❌ Ingestion Failed for {category}: {e}")

    print(f"✅ Ingestion Cycle Complete. Total businesses tracked: {total_new}")

if __name__ == "__main__":
    ingest_businesses()
