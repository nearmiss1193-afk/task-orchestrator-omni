"""
PROSPECTOR ENGINE v1 — Multi-Source Lead Discovery
Runs as Modal cron every 6 hours. Autonomous pipeline:

  1. DISCOVER: Google Places API (Text Search) finds businesses by niche + city
  2. ENRICH: Hunter.io domain search + website contact page scraping for emails
  3. DEDUPLICATE: Checks contacts_master by phone AND business name
  4. INSERT: New leads go in with status='new', ready for outreach

Searches rotate through niches × cities to avoid re-scraping same results.
Uses cycle_index (stored in system_state) to track position.
"""
import os
import re
import sys
import time
import json
import hashlib
import requests
from datetime import datetime, timezone

if "/root" not in sys.path:
    sys.path.append("/root")


# ============================================================
#  CONFIGURATION: Niches × Cities = Search Matrix
# ============================================================

# Fallback list if DB is empty
DEFAULT_NICHES = [
    # === TIER 1: "BLEEDING LEADS" ===
    "tree removal service",
    "gutter installation",
    "pool service company",
    "lawn care service",
    "HVAC contractor",
    "plumbing company",
    "roofing contractor",
    "electrician",
    "pest control company",
    "locksmith",
    "towing service",
    # === OVERRIDES WILL BE INJECTED BY AUTONOMOUS TUNING ===
]

CITIES = [
    # === FLORIDA: Central FL (Home Market) ===
    # Ring 0: Lakeland Core
    "Lakeland FL",
    "33801", "33803", "33805", "33809", "33810",
    "33811", "33812", "33813", "33815",
    # Ring 1: Polk County
    "Winter Haven FL", "Bartow FL", "Auburndale FL",
    "Lake Wales FL", "Haines City FL", "Davenport FL",
    "Mulberry FL", "Eagle Lake FL",
    # Ring 2: Adjacent Counties
    "Plant City FL", "Brandon FL", "Riverview FL",
    "Kissimmee FL", "St Cloud FL", "Poinciana FL",
    "Sebring FL", "Avon Park FL", "Wauchula FL",
    "Zephyrhills FL", "Dade City FL",
    # Ring 3: Metro Areas
    "Tampa FL", "St Petersburg FL", "Clearwater FL",
    "Orlando FL", "Sanford FL", "Clermont FL",
    "Leesburg FL", "Ocala FL", "Bradenton FL", "Sarasota FL",
    # Ring 4: Extended
    "Daytona Beach FL", "Melbourne FL", "Fort Myers FL",
    "Naples FL", "Gainesville FL", "The Villages FL",

    # === MOUNTAIN: Denver / Phoenix / Vegas / SLC ===
    # Denver Metro
    "Denver CO", "Aurora CO", "Lakewood CO", "Arvada CO",
    "Westminster CO", "Thornton CO", "Boulder CO",
    "Fort Collins CO", "Colorado Springs CO",
    # Phoenix Metro
    "Phoenix AZ", "Scottsdale AZ", "Mesa AZ", "Tempe AZ",
    "Chandler AZ", "Gilbert AZ", "Glendale AZ", "Peoria AZ",
    "Tucson AZ",
    # Las Vegas Metro
    "Las Vegas NV", "Henderson NV", "North Las Vegas NV", "Reno NV",
    # Salt Lake City Metro
    "Salt Lake City UT", "Provo UT", "Ogden UT", "Sandy UT",
    # Other Mountain
    "Albuquerque NM", "Santa Fe NM", "Boise ID",

    # === WEST COAST: LA / SF / San Diego / Portland / Seattle ===
    # Los Angeles Metro
    "Los Angeles CA", "Long Beach CA", "Pasadena CA",
    "Burbank CA", "Santa Monica CA", "Torrance CA",
    "Irvine CA", "Anaheim CA", "Riverside CA",
    "Ontario CA", "San Bernardino CA",
    # San Diego Metro
    "San Diego CA", "Chula Vista CA", "Oceanside CA", "Escondido CA",
    # San Francisco / Bay Area
    "San Francisco CA", "Oakland CA", "San Jose CA",
    "Fremont CA", "Sunnyvale CA", "Santa Rosa CA",
    "Sacramento CA", "Stockton CA",
    # Portland Metro
    "Portland OR", "Beaverton OR", "Salem OR", "Eugene OR",
    # Seattle Metro
    "Seattle WA", "Tacoma WA", "Bellevue WA", "Everett WA",
    "Spokane WA",
]

# Region lookup for market comparison analytics
CITY_REGIONS = {}
_region_map = {
    "florida": [
        "Lakeland FL", "33801", "33803", "33805", "33809", "33810",
        "33811", "33812", "33813", "33815",
        "Winter Haven FL", "Bartow FL", "Auburndale FL",
        "Lake Wales FL", "Haines City FL", "Davenport FL",
        "Mulberry FL", "Eagle Lake FL",
        "Plant City FL", "Brandon FL", "Riverview FL",
        "Kissimmee FL", "St Cloud FL", "Poinciana FL",
        "Sebring FL", "Avon Park FL", "Wauchula FL",
        "Zephyrhills FL", "Dade City FL",
        "Tampa FL", "St Petersburg FL", "Clearwater FL",
        "Orlando FL", "Sanford FL", "Clermont FL",
        "Leesburg FL", "Ocala FL", "Bradenton FL", "Sarasota FL",
        "Daytona Beach FL", "Melbourne FL", "Fort Myers FL",
        "Naples FL", "Gainesville FL", "The Villages FL",
    ],
    "mountain": [
        "Denver CO", "Aurora CO", "Lakewood CO", "Arvada CO",
        "Westminster CO", "Thornton CO", "Boulder CO",
        "Fort Collins CO", "Colorado Springs CO",
        "Phoenix AZ", "Scottsdale AZ", "Mesa AZ", "Tempe AZ",
        "Chandler AZ", "Gilbert AZ", "Glendale AZ", "Peoria AZ",
        "Tucson AZ",
        "Las Vegas NV", "Henderson NV", "North Las Vegas NV", "Reno NV",
        "Salt Lake City UT", "Provo UT", "Ogden UT", "Sandy UT",
        "Albuquerque NM", "Santa Fe NM", "Boise ID",
    ],
    "west_coast": [
        "Los Angeles CA", "Long Beach CA", "Pasadena CA",
        "Burbank CA", "Santa Monica CA", "Torrance CA",
        "Irvine CA", "Anaheim CA", "Riverside CA",
        "Ontario CA", "San Bernardino CA",
        "San Diego CA", "Chula Vista CA", "Oceanside CA", "Escondido CA",
        "San Francisco CA", "Oakland CA", "San Jose CA",
        "Fremont CA", "Sunnyvale CA", "Santa Rosa CA",
        "Sacramento CA", "Stockton CA",
        "Portland OR", "Beaverton OR", "Salem OR", "Eugene OR",
        "Seattle WA", "Tacoma WA", "Bellevue WA", "Everett WA",
        "Spokane WA",
    ],
}
for region, cities in _region_map.items():
    for city in cities:
        CITY_REGIONS[city] = region

# How many search combos to run per cycle (400 = ~12 min runtime)
SEARCHES_PER_CYCLE = 400

# Max leads to insert per cycle
MAX_INSERTS_PER_CYCLE = 5000


# ============================================================
#  STAGE 1: DISCOVER — Google Places API
# ============================================================

def discover_businesses(query: str, api_key: str) -> list:
    """
    Uses Google Places Text Search to find businesses.
    Returns raw business data with name, address, phone, website, place_id.
    """
    if not api_key:
        print(f"  ⚠️ No GOOGLE_PLACES_API_KEY — skipping Google discovery")
        return []

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": api_key}

    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != "OK":
            print(f"  ⚠️ Places API status: {data.get('status')} — {data.get('error_message', '')}")
            return []

        leads = []
        for place in data.get("results", [])[:20]:
            # Get details (phone + website)
            details = _get_place_details(place["place_id"], api_key)

            lead = {
                "business_name": place.get("name", ""),
                "location": place.get("formatted_address", ""),
                "phone": details.get("formatted_phone_number", ""),
                "website_url": details.get("website", ""),
                "google_rating": place.get("rating"),
                "google_reviews": place.get("user_ratings_total"),
                "place_id": place.get("place_id"),
                "source": "google_places",
            }
            leads.append(lead)
            time.sleep(0.1)  # Gentle rate limiting on details calls

        print(f"  📍 Google Places: found {len(leads)} businesses")
        return leads

    except Exception as e:
        print(f"  ❌ Google Places error: {e}")
        return []


def _get_place_details(place_id: str, api_key: str) -> dict:
    """Fetch phone + website from Place Details API."""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website,opening_hours",
        "key": api_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        return resp.json().get("result", {})
    except:
        return {}


# ============================================================
#  STAGE 2: ENRICH — Find emails via Hunter.io + website scrape
# ============================================================

def enrich_with_email(lead: dict, hunter_key: str) -> dict:
    """
    Multi-method email discovery:
    1. Hunter.io domain search (if API key available)
    2. Website contact page scraping (always attempted)
    Returns the lead dict with 'email' and 'contact_name' added.
    """
    website = lead.get("website_url", "")
    if not website:
        return lead  # Can't enrich without website

    domain = _extract_domain(website)
    if not domain:
        return lead

    # --- Method 1: Hunter.io ---
    if hunter_key and hunter_key != "***REMOVED***":
        email, name = _hunter_domain_search(domain, hunter_key)
        if email:
            lead["email"] = email
            lead["contact_name"] = name or ""
            lead["email_source"] = "hunter.io"
            print(f"    📧 Hunter.io found: {email}")
            return lead

    # --- Method 2: Website scrape ---
    email = _scrape_website_for_email(website)
    if email:
        lead["email"] = email
        lead["email_source"] = "website_scrape"
        print(f"    📧 Website scrape found: {email}")
        return lead

    return lead


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    url = url.lower().replace("http://", "").replace("https://", "").replace("www.", "")
    return url.split("/")[0].split("?")[0].strip()


def _hunter_domain_search(domain: str, api_key: str) -> tuple:
    """Use Hunter.io to find the most relevant email for a domain."""
    try:
        url = "https://api.hunter.io/v2/domain-search"
        params = {"domain": domain, "api_key": api_key, "limit": 3}
        resp = requests.get(url, params=params, timeout=10)

        if resp.status_code == 200:
            data = resp.json().get("data", {})
            emails = data.get("emails", [])
            if emails:
                # Prefer owner / decision-maker roles
                priority_roles = ["owner", "ceo", "founder", "president", "director", "manager", "general"]
                for role in priority_roles:
                    for e in emails:
                        position = (e.get("position") or "").lower()
                        if role in position:
                            full_name = f"{e.get('first_name', '')} {e.get('last_name', '')}".strip()
                            return e["value"], full_name

                # Fallback: first email
                e = emails[0]
                full_name = f"{e.get('first_name', '')} {e.get('last_name', '')}".strip()
                return e["value"], full_name

        elif resp.status_code == 429:
            print(f"    ⚠️ Hunter.io rate limited")

    except Exception as e:
        print(f"    ⚠️ Hunter.io error: {e}")

    return None, None


def _scrape_website_for_email(url: str) -> str:
    """Scrape the website homepage + /contact page for email addresses."""
    emails_found = set()

    for page_url in [url, url.rstrip("/") + "/contact", url.rstrip("/") + "/contact-us"]:
        try:
            resp = requests.get(page_url, timeout=8, headers={
                "User-Agent": "Mozilla/5.0 (compatible; BusinessBot/1.0)"
            }, allow_redirects=True)
            if resp.status_code == 200:
                # Extract emails from page text
                page_emails = re.findall(
                    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
                    resp.text
                )
                for e in page_emails:
                    e_lower = e.lower()
                    # Skip generic/spam addresses
                    if not any(skip in e_lower for skip in [
                        'example.com', 'test.com', 'sentry', 'webpack',
                        'noreply', 'no-reply', 'wixpress', 'squarespace',
                        'wordpress', '.png', '.jpg', '.gif', '.svg',
                        'schema.org', 'json', 'cloudflare'
                    ]):
                        emails_found.add(e_lower)
        except:
            pass

    if emails_found:
        # Prefer info@, contact@, hello@ (business emails)
        priority_prefixes = ['info@', 'contact@', 'hello@', 'office@', 'admin@']
        for prefix in priority_prefixes:
            for e in emails_found:
                if e.startswith(prefix):
                    return e
        # Return first found
        return list(emails_found)[0]

    return None


# ============================================================
#  STAGE 2.5: SCORE — Calculate vulnerability score
# ============================================================

def calculate_lead_score(lead: dict) -> int:
    """
    Calculates the 'Bleeding Lead' score (0-10).
    +3: Review count < 50 (Identity gap)
    +2: Rating < 4.5 (Reputation gap)
    +3: No website (Digital gap)
    +2: Tier 1 Vertical (High-stakes gap)
    """
    score = 0
    
    # Review Count Gap
    reviews = lead.get("google_reviews") or 0
    if reviews < 50:
        score += 3
    elif reviews < 100:
        score += 1
        
    # Rating Gap
    rating = lead.get("google_rating") or 5.0
    if rating < 4.5:
        score += 2
        
    # Digital Gap
    if not lead.get("website_url"):
        score += 3
        
    # Vertical Priority
    tier1 = ["tree", "gutter", "pool", "lawn", "hvac", "plumbing", "roofing"]
    name_low = lead.get("business_name", "").lower()
    if any(v in name_low for v in tier1):
        score += 2
        
    return min(score, 10)


# ============================================================
#  STAGE 3: DEDUPLICATE + INSERT
# ============================================================

def is_duplicate(supabase, phone: str, business_name: str, email: str) -> bool:
    """Check if lead already exists in contacts_master."""
    try:
        # Check by phone (most reliable)
        if phone:
            clean = re.sub(r'[^\d]', '', phone)
            if len(clean) >= 10:
                result = supabase.table("contacts_master").select("id").ilike(
                    "phone", f"%{clean[-10:]}%"
                ).limit(1).execute()
                if result.data:
                    return True

        # Check by email
        if email and email != "notfound@example.com":
            result = supabase.table("contacts_master").select("id").eq(
                "email", email
            ).limit(1).execute()
            if result.data:
                return True

        # Check by company name (fuzzy)
        if business_name and len(business_name) > 3:
            result = supabase.table("contacts_master").select("id").ilike(
                "company_name", f"%{business_name}%"
            ).limit(1).execute()
            if result.data:
                return True

    except Exception as e:
        print(f"    ⚠️ Dedup check error: {e}")

    return False


def insert_lead(supabase, lead: dict, niche: str, city: str) -> bool:
    """Insert a new lead into contacts_master."""
    try:
        import uuid
        region = CITY_REGIONS.get(city, "florida")
        record = {
            "ghl_contact_id": f"prospector-{uuid.uuid4().hex[:12]}",
            "company_name": lead.get("business_name", ""),
            "full_name": lead.get("contact_name", "") or "",
            "phone": lead.get("phone", ""),
            "email": lead.get("email", ""),
            "website_url": lead.get("website_url", ""),
            "niche": niche,
            "status": "new",
            "source": lead.get("source", "prospector"),
            "lead_source": f"google_places_{region}",
            "raw_research": json.dumps({
                "google_rating": lead.get("google_rating"),
                "google_reviews": lead.get("google_reviews"),
                "email_source": lead.get("email_source", ""),
                "place_id": lead.get("place_id", ""),
                "location": lead.get("location", ""),
                "region": region,
                "prospected_at": datetime.now(timezone.utc).isoformat(),
                "search_query": f"{niche} {city}",
            }),
        }

        supabase.table("contacts_master").insert(record).execute()
        return True

    except Exception as e:
        print(f"    ❌ Insert error: {e}")
        return False


# ============================================================
#  CYCLE MANAGEMENT: Rotate through search matrix
# ============================================================

def get_cycle_index(supabase) -> int:
    """Get current position in the search matrix from system_state."""
    try:
        result = supabase.table("system_state").select("*").eq("key", "prospector_cycle_index").execute()
        if result.data:
            return int(result.data[0].get("last_error", 0) or 0)
    except:
        pass
    return 0


def save_cycle_index(supabase, index: int):
    """Save current position in the search matrix."""
    try:
        supabase.table("system_state").upsert({
            "key": "prospector_cycle_index",
            "status": "working",
            "last_error": str(index),
        }, on_conflict="key").execute()
    except Exception as e:
        print(f"  ⚠️ Failed to save cycle index: {e}")


# ============================================================
#  MAIN ENTRY POINT
# ============================================================

def run_prospecting_cycle():
    """
    Main prospecting cycle. Called by Modal cron every 6 hours.
    Rotates through niche×city combos, discovers, enriches, inserts.
    """
    from modules.database.supabase_client import get_supabase

    print(f"\n{'='*60}")
    print(f"🔍 PROSPECTOR ENGINE v1 — {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}")

    supabase = get_supabase()
    api_keys = [os.environ.get("GOOGLE_API_KEY"), os.environ.get("GOOGLE_PLACES_API_KEY")]
    api_keys = [k for k in api_keys if k]
    if not api_keys:
        print("  ⚠️ Missing GOOGLE_API_KEY or GOOGLE_PLACES_API_KEY environment variable")
        # Ensure we don't proceed with an empty or old key
        return None
    hunter_key = os.environ.get("HUNTER_API_KEY", "")
    
    # Debug: show which key is being used
    print(f"🔑 Google Places key: {api_keys[0][:12]}...")

    # Fetch Dynamic Niches (Phase 6 Tuning)
    active_niches = DEFAULT_NICHES
    try:
        db_niches = supabase.table("system_state").select("last_error").eq("key", "prospector_dynamic_niches").execute()
        if db_niches.data and db_niches.data[0].get("last_error"):
            parsed = json.loads(db_niches.data[0]["last_error"])
            if isinstance(parsed, list) and len(parsed) > 0:
                print(f"🧠 AI Tuning Active: Loaded {len(parsed)} dynamic niches from database")
                active_niches = parsed
    except Exception as e:
        print(f"  ⚠️ Failed to load dynamic niches, falling back to defaults: {e}")

    # Build search matrix
    search_combos = [(niche, city) for city in CITIES for niche in active_niches]
    total_combos = len(search_combos)
    print(f"📊 Search matrix: {len(active_niches)} niches × {len(CITIES)} cities = {total_combos} combos")

    # Resume from last position
    cycle_index = get_cycle_index(supabase)
    print(f"📍 Resuming from index {cycle_index}/{total_combos}")

    # Stats
    total_discovered = 0
    total_enriched = 0
    total_inserted = 0
    total_duplicates = 0
    total_no_contact = 0

    # Run SEARCHES_PER_CYCLE searches
    searches_done = 0
    while searches_done < SEARCHES_PER_CYCLE and total_inserted < MAX_INSERTS_PER_CYCLE:
        # Wrap around
        idx = cycle_index % total_combos
        niche, city = search_combos[idx]
        cycle_index += 1
        searches_done += 1

        query = f"{niche} {city}"
        print(f"\n🔎 [{searches_done}/{SEARCHES_PER_CYCLE}] Searching: {query}")

        # Stage 1: Discover
        raw_leads = discover_businesses(query, google_key)
        total_discovered += len(raw_leads)

        for lead in raw_leads:
            if total_inserted >= MAX_INSERTS_PER_CYCLE:
                break

            # Stage 2: Enrich
            lead = enrich_with_email(lead, hunter_key)

            # Stage 2.5: Score
            lead["score"] = calculate_lead_score(lead)

            has_email = bool(lead.get("email"))
            has_phone = bool(lead.get("phone"))

            if has_email:
                total_enriched += 1

            if not has_email and not has_phone:
                total_no_contact += 1
                continue  # Skip leads with no contact info at all

            # Stage 3: Dedup + Insert
            biz_name = lead.get("business_name", "")
            if is_duplicate(supabase, lead.get("phone", ""), biz_name, lead.get("email", "")):
                total_duplicates += 1
                continue

            if insert_lead(supabase, lead, niche, city):
                total_inserted += 1
                status = "📧" if has_email else "📞"
                print(f"  ✅ {status} Inserted: {biz_name}")

        # Rate limit between searches
        if searches_done < SEARCHES_PER_CYCLE:
            time.sleep(2)

    # Save position for next cycle
    save_cycle_index(supabase, cycle_index)

    # Summary
    print(f"\n{'='*60}")
    print(f"📈 PROSPECTOR RESULTS:")
    print(f"   Discovered: {total_discovered}")
    print(f"   Enriched (with email): {total_enriched}")
    print(f"   Inserted: {total_inserted}")
    print(f"   Duplicates skipped: {total_duplicates}")
    print(f"   No contact info: {total_no_contact}")
    print(f"   Next cycle index: {cycle_index}/{total_combos}")
    print(f"{'='*60}\n")

    # Log to system_health
    try:
        import uuid
        supabase.table("system_health_log").insert({
            "id": str(uuid.uuid4()),
            "check_type": "prospector",
            "status": "prospecting_complete",
            "details": json.dumps({
                "discovered": total_discovered,
                "enriched": total_enriched,
                "inserted": total_inserted,
                "duplicates": total_duplicates,
                "no_contact": total_no_contact,
                "cycle_index": cycle_index,
                "searches_run": searches_done,
            }),
        }).execute()
    except:
        pass

    return {
        "discovered": total_discovered,
        "enriched": total_enriched,
        "inserted": total_inserted,
        "duplicates": total_duplicates,
    }
