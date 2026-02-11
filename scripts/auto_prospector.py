"""
AUTO PROSPECTOR v3 — Browser-based Google Maps scraping
Uses requests to hit Google Maps search and extract business info.
Falls back to direct website scraping for email extraction.
"""
import os
import sys
import json
import time
import requests
import re
from datetime import datetime, timezone

sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')

from supabase import create_client

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CURATED FLORIDA HOME SERVICE BUSINESSES ---
# Direct list approach: known businesses + their websites
# More reliable than search scraping
PROSPECTS = [
    # HVAC - Tampa/Central FL
    {"name": "Hays Cooling Heating & Plumbing", "website": "https://www.haysusa.com", "niche": "HVAC contractor", "city": "Phoenix AZ"},
    {"name": "Pro-Tech Air Conditioning", "website": "https://www.protechac.com", "niche": "HVAC contractor", "city": "Tampa FL"},
    {"name": "Gulf Shore Cooling", "website": "https://www.gulfshorecooling.com", "niche": "HVAC contractor", "city": "Naples FL"},
    {"name": "Comfort Temp", "website": "https://www.comforttemp.com", "niche": "HVAC contractor", "city": "Gainesville FL"},
    {"name": "Sun State Air Conditioning", "website": "https://www.sunstateac.com", "niche": "HVAC contractor", "city": "Jacksonville FL"},
    {"name": "Energy Air", "website": "https://www.energyair.com", "niche": "HVAC contractor", "city": "Orlando FL"},
    {"name": "Colman Heating & Air", "website": "https://www.colmanheatingandair.com", "niche": "HVAC contractor", "city": "Brevard FL"},
    {"name": "One Hour Air Orlando", "website": "https://www.onehourairorlandofl.com", "niche": "HVAC contractor", "city": "Orlando FL"},
    {"name": "Del-Air Heating and Air Conditioning", "website": "https://www.delair.com", "niche": "HVAC contractor", "city": "Sanford FL"},
    {"name": "Climate Experts Air", "website": "https://www.climateexpertsair.com", "niche": "HVAC contractor", "city": "Melbourne FL"},
    
    # Plumbing - Florida
    {"name": "Roto-Rooter Tampa", "website": "https://www.rotorooter.com", "niche": "plumbing company", "city": "Tampa FL"},
    {"name": "Alvarez Plumbing", "website": "https://www.alvarezplumbing.com", "niche": "plumbing company", "city": "Salinas CA"},
    {"name": "Clog Kings", "website": "https://www.clogkings.com", "niche": "plumbing company", "city": "Miami FL"},
    {"name": "Bill Fenwick Plumbing", "website": "https://www.billfenwick.com", "niche": "plumbing company", "city": "Jacksonville FL"},
    {"name": "Aztec Plumbing", "website": "https://www.aztecplumbing.net", "niche": "plumbing company", "city": "Fort Myers FL"},
    {"name": "Sun Plumbing", "website": "https://www.sunplumbing.com", "niche": "plumbing company", "city": "Melbourne FL"},
    {"name": "Sewer Pros", "website": "https://www.sewerpros.com", "niche": "plumbing company", "city": "Orlando FL"},
    {"name": "My Plumber SA", "website": "https://www.myplumbersa.com", "niche": "plumbing company", "city": "San Antonio TX"},
    
    # Roofing - Florida
    {"name": "Universal Roof & Contracting", "website": "https://www.universalroof.com", "niche": "roofing contractor", "city": "Orlando FL"},
    {"name": "Code Engineered Systems", "website": "https://www.caboroof.com", "niche": "roofing contractor", "city": "Tampa FL"},
    {"name": "Mighty Dog Roofing", "website": "https://www.mightydogroofing.com", "niche": "roofing contractor", "city": "Tampa FL"},
    {"name": "Westfall Roofing", "website": "https://www.westfallroofing.com", "niche": "roofing contractor", "city": "Tampa FL"},
    {"name": "Done Rite Roofing", "website": "https://www.doneriteroofinginc.com", "niche": "roofing contractor", "city": "Clearwater FL"},
    {"name": "Earl W Johnston Roofing", "website": "https://www.ewjroofing.com", "niche": "roofing contractor", "city": "Hollywood FL"},
    
    # Electrical - Florida  
    {"name": "Mister Sparky Tampa", "website": "https://www.mistersparky.com", "niche": "electrical contractor", "city": "Tampa FL"},
    {"name": "ServiceMaster Restore", "website": "https://www.servicemaster.com", "niche": "electrical contractor", "city": "Orlando FL"},
    {"name": "Wirenut Electric", "website": "https://www.callwirenut.com", "niche": "electrical contractor", "city": "Orlando FL"},
    
    # Pest Control - Florida
    {"name": "Nozzle Nolen", "website": "https://www.nozzlenolen.com", "niche": "pest control company", "city": "West Palm Beach FL"},
    {"name": "Florida Pest Control", "website": "https://www.floridapestcontrol.com", "niche": "pest control company", "city": "Gainesville FL"},
    {"name": "Hulett Environmental Services", "website": "https://www.hulettinc.com", "niche": "pest control company", "city": "West Palm Beach FL"},
    {"name": "Massey Services", "website": "https://www.masseyservices.com", "niche": "pest control company", "city": "Orlando FL"},
    {"name": "Turner Pest Control", "website": "https://www.turnerpest.com", "niche": "pest control company", "city": "Jacksonville FL"},
    
    # Pool / Landscaping - Florida
    {"name": "Pool Troopers", "website": "https://www.pooltroopers.com", "niche": "pool service company", "city": "Tampa FL"},
    {"name": "ABC Pool Service", "website": "https://www.abcpoolservice.com", "niche": "pool service company", "city": "Fort Lauderdale FL"},
    {"name": "BrightView Landscapes", "website": "https://www.brightview.com", "niche": "landscaping company", "city": "Orlando FL"},
    {"name": "Down To Earth Landscape", "website": "https://www.dtefl.com", "niche": "landscaping company", "city": "Orlando FL"},
    
    # Garage Door / Painting / Pressure Washing
    {"name": "Precision Door Service", "website": "https://www.precisiondoor.net", "niche": "garage door repair", "city": "Tampa FL"},
    {"name": "CertaPro Painters Tampa", "website": "https://www.certapro.com", "niche": "painting contractor", "city": "Tampa FL"},
    {"name": "Prolific Powerhouse", "website": "https://www.prolificpowerhouse.com", "niche": "pressure washing service", "city": "Orlando FL"},
    {"name": "ProClean Pressure Washing", "website": "https://www.procleanpw.com", "niche": "pressure washing service", "city": "Tampa FL"},
]


def extract_emails_from_url(url: str) -> list:
    """Scrape a webpage and extract email addresses."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        if r.status_code != 200:
            return []
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = list(set(re.findall(email_pattern, r.text)))
        
        skip = ['example.com', 'email.com', 'domain.com', 'sentry.io',
                'wixpress.com', 'googleapis.com', 'schema.org', 'w3.org',
                '.png', '.jpg', '.gif', '.svg', 'wordpress.org', 'gravatar.com',
                'jquery.com', 'cloudflare.com', 'gstatic.com', 'google.com',
                'yoursite.com', 'yourdomain', 'test@', 'noreply']
        emails = [e for e in emails if not any(s in e.lower() for s in skip)]
        
        return emails[:3]
    except Exception as ex:
        print(f"    Email extraction error for {url}: {ex}")
        return []


def is_duplicate(website_url: str, email: str) -> bool:
    """Check if lead already exists."""
    try:
        if website_url:
            # Check by domain (strip protocol)
            domain = website_url.replace('https://', '').replace('http://', '').rstrip('/')
            existing = supabase.table("contacts_master").select("id").ilike("website_url", f"%{domain}%").limit(1).execute()
            if existing.data:
                return True
        if email:
            existing = supabase.table("contacts_master").select("id").eq("email", email).limit(1).execute()
            if existing.data:
                return True
    except Exception:
        pass
    return False


def run_prospecting():
    """Process curated prospect list — extract emails and insert."""
    print("=" * 60)
    print("  AUTO PROSPECTOR v3 — Curated Florida Business List")
    print("=" * 60)
    
    inserted = 0
    skipped_dup = 0
    skipped_noemail = 0
    
    for p in PROSPECTS:
        name = p["name"]
        website = p["website"]
        niche = p["niche"]
        city = p.get("city", "Florida")
        
        print(f"\n  Processing: {name} ({website})")
        
        # Check duplicate first
        if is_duplicate(website, None):
            print(f"    Skip: already in DB")
            skipped_dup += 1
            continue
        
        # Extract emails from homepage
        emails = extract_emails_from_url(website)
        
        # Try contact page if no email on homepage
        if not emails:
            for path in ['/contact', '/contact-us', '/about', '/about-us']:
                emails = extract_emails_from_url(website.rstrip('/') + path)
                if emails:
                    break
        
        if not emails:
            print(f"    Skip: no email found")
            skipped_noemail += 1
            continue
        
        email = emails[0]
        
        # Check email duplicate
        if is_duplicate(None, email):
            print(f"    Skip: email {email} already in DB")
            skipped_dup += 1
            continue
        
        # Insert into contacts_master
        lead = {
            "company_name": name,
            "website_url": website,
            "email": email,
            "niche": niche,
            "status": "new",
            "funnel_stage": "new",
            "source": "auto_prospect_v3",
        }
        
        try:
            supabase.table("contacts_master").insert(lead).execute()
            inserted += 1
            print(f"    ✅ INSERTED: {email}")
        except Exception as e:
            print(f"    ❌ DB Error: {e}")
        
        time.sleep(1)  # Rate limiting
    
    print(f"\n{'=' * 60}")
    print(f"  RESULTS")
    print(f"{'=' * 60}")
    print(f"  Total processed: {len(PROSPECTS)}")
    print(f"  Inserted: {inserted}")
    print(f"  Skipped (duplicate): {skipped_dup}")
    print(f"  Skipped (no email): {skipped_noemail}")
    print(f"\n  All new leads have website + email -> AUDIT PIPELINE READY")


if __name__ == "__main__":
    run_prospecting()
