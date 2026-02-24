"""
Phase 24: Autonomous Prospector Daemon
Checks if 'new' leads < 50. If so, scrapes Google Places for a random niche + city.
Extracts emails, deduplicates against CRM, and inserts 100 new targets.
"""
import os
import sys
import time
import requests
import re
import random
from dotenv import load_dotenv

sys.path.insert(0, '.')
load_dotenv('.env')
load_dotenv('.env.local')

from supabase import create_client

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

GOOGLE_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

NICHES = [
    "plumber", "roofer", "hvac", "electrician", "landscaping",
    "pest control", "tree service", "pressure washing", "pool cleaning",
    "garage door repair", "attorney", "dentist", "med spa", "chiropractor"
]

CITIES = [
    "Orlando FL", "Tampa FL", "Jacksonville FL", "Miami FL", 
    "St Petersburg FL", "Clearwater FL", "Lakeland FL", "Fort Myers FL",
    "Sarasota FL", "Naples FL", "Bradenton FL", "Kissimmee FL",
    "Ocala FL", "Gainesville FL", "Daytona Beach FL", "Melbourne FL"
]

def extract_emails_from_url(url: str) -> list:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if r.status_code != 200:
            return []
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = list(set(re.findall(email_pattern, r.text)))
        skip = ['example.com', 'email.com', 'domain.com', '.png', '.jpg', 'wixpress.com']
        emails = [e for e in emails if not any(s in e.lower() for s in skip)]
        return emails[:2]
    except Exception:
        return []

def search_places(query, page_token=None):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_KEY}
    if page_token:
        params["pagetoken"] = page_token
    r = requests.get(url, params=params, timeout=15)
    data = r.json()
    return data.get("results", []), data.get("next_page_token")

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"place_id": place_id, "fields": "formatted_phone_number,website", "key": GOOGLE_KEY}
    r = requests.get(url, params=params, timeout=15)
    return r.json().get("result", {})

def is_duplicate(domain: str, email: str, phone: str) -> bool:
    try:
        if phone:
            digits = re.sub(r'\D', '', phone)
            if len(digits) >= 10:
                phone_like = f"%{digits[-10:]}%"
                res = supabase.table("contacts_master").select("id").ilike("phone", phone_like).limit(1).execute()
                if res.data: return True
        if domain:
            dom = domain.replace('https://', '').replace('http://', '').replace('www.', '').rstrip('/')
            res = supabase.table("contacts_master").select("id").ilike("website_url", f"%{dom}%").limit(1).execute()
            if res.data: return True
        if email:
            res = supabase.table("contacts_master").select("id").eq("email", email).limit(1).execute()
            if res.data: return True
    except Exception:
        pass
    return False

def run_autonomous_prospector():
    print("==================================================")
    print("🤖 AUTONOMOUS PROSPECTOR TRIGGERED")
    print("==================================================")
    
    # Check current pipeline
    try:
        res = supabase.table("contacts_master").select("id", count="exact").eq("status", "new").execute()
        new_count = res.count
    except Exception as e:
        print(f"❌ Error checking CRM count: {e}")
        return
        
    print(f"📊 Current 'new' leads: {new_count}")
    if new_count >= 50:
        print("✅ Pipeline healthy. Prospector returning to sleep.")
        return
        
    print("📉 Pipeline below 50. Initiating hunt...")
    
    # Pick a random niche and city
    niche = random.choice(NICHES)
    city = random.choice(CITIES)
    query = f"{niche} in {city}"
    print(f"🔍 Target Vector: {query}")
    
    results, next_token = search_places(query)
    if not results:
        print("❌ No results found from Google Maps.")
        return
        
    found_count = 0
    pages_scraped = 0
    
    while True:
        pages_scraped += 1
        for r in results:
            if found_count >= 100:
                break
                
            name = r.get("name", "")
            pid = r.get("place_id", "")
            if not pid: continue
            
            details = get_place_details(pid)
            phone = details.get("formatted_phone_number", "")
            website = details.get("website", "")
            
            if not phone: continue
            
            email = ""
            if website:
                emails = extract_emails_from_url(website)
                if not emails:
                    for path in ['/contact', '/contact-us']:
                        emails = extract_emails_from_url(website.rstrip('/') + path)
                        if emails: break
                if emails: email = emails[0]
                
            if is_duplicate(website, email, phone):
                print(f"  [DUP] Skipping {name}")
                continue
                
            # Insert new lead
            lead = {
                "company_name": name,
                "phone": phone,
                "website_url": website,
                "email": email,
                "niche": niche.title(),
                "status": "new",
                "funnel_stage": "new",
                "source": "autonomous_prospector"
            }
            try:
                supabase.table("contacts_master").insert(lead).execute()
                found_count += 1
                if email:
                    print(f"  ✅ INJECTED [EMAIL]: {name}")
                else:
                    print(f"  ✅ INJECTED [SMS-ONLY]: {name}")
            except Exception as e:
                print(f"  ❌ DB Error: {e}")
                
        if found_count >= 100 or not next_token or pages_scraped >= 3:
            break
            
        time.sleep(2)
        results, next_token = search_places(query, next_token)
        
    print(f"🏁 Hunt Complete. Secured {found_count} new B2B targets.")

if __name__ == "__main__":
    run_autonomous_prospector()
