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

NICHES = [
    # === TIER 1: HIGH NEED (miss calls, need AI receptionist) ===
    "HVAC contractor",
    "plumbing company",
    "roofing contractor",
    "electrician",
    "pest control company",
    "locksmith",
    "towing service",
    "auto repair shop",
    "garage door repair",
    # === TIER 2: APPOINTMENT-BASED (need booking automation) ===
    "dental clinic",
    "chiropractic clinic",
    "veterinary clinic",
    "medical spa",
    "optometrist",
    "physiotherapist",
    "massage therapist",
    "counseling center",
    # === TIER 3: ALL TRADES (small shops that don't answer) ===
    "sign shop",
    "mechanic",
    "welding shop",
    "concrete contractor",
    "paving company",
    "glass repair",
    "gutter installation",
    "fence company",
    "flooring company",
    "cabinet maker",
    "tile installer",
    "drywall contractor",
    "stucco contractor",
    "waterproofing company",
    "screen enclosure",
    "window installation",
    "door repair",
    "septic tank service",
    "well drilling",
    "irrigation company",
    "landscaping company",
    "pool service company",
    "tree removal service",
    "pressure washing service",
    "lawn care service",
    "painting contractor",
    "remodeler",
    "general contractor",
    "handyman service",
    "solar panel installation",
    "home security company",
    # === TIER 4: VOLUME (high call volume, low staff) ===
    "hair salon",
    "barber shop",
    "nails salon",
    "pet grooming",
    "dog grooming",
    "cleaning service",
    "carpet cleaning",
    "window cleaning",
    "junk removal",
    "moving company",
    "storage facility",
    "auto detailing",
    "car wash",
    "tire shop",
    "transmission shop",
    "body shop",
    "tint shop",
    # === TIER 5: SERVICE BUSINESSES ===
    "tattoo shop",
    "fitness center",
    "martial arts school",
    "dance studio",
    "daycare center",
    "preschool",
    "tutoring center",
    "driving school",
    "music lessons",
    "yoga studio",
    "florist",
    "bakery",
    "catering service",
    "food truck",
    "print shop",
    "embroidery shop",
    "trophy shop",
    "appliance repair",
    # === TIER 6: PROFESSIONAL (higher value) ===
    "law firm",
    "accounting firm",
    "insurance agency",
    "real estate agency",
    "mortgage broker",
    "financial advisor",
    "staffing agency",
    "IT support company",
]

CITIES = [
    # === RING 0: Lakeland Core (0-10 mi) ===
    "Lakeland FL",
    "33801", "33803", "33805", "33809", "33810",
    "33811", "33812", "33813", "33815",
    # === RING 1: Polk County (10-25 mi) ===
    "Winter Haven FL",
    "Bartow FL",
    "Auburndale FL",
    "Lake Wales FL",
    "Haines City FL",
    "Davenport FL",
    "Mulberry FL",
    "Eagle Lake FL",
    # === RING 2: Adjacent Counties (25-50 mi) ===
    "Plant City FL",
    "Brandon FL",
    "Riverview FL",
    "Kissimmee FL",
    "St Cloud FL",
    "Poinciana FL",
    "Sebring FL",
    "Avon Park FL",
    "Wauchula FL",
    "Zephyrhills FL",
    "Dade City FL",
    # === RING 3: Metro Areas (50-75 mi) ===
    "Tampa FL",
    "St Petersburg FL",
    "Clearwater FL",
    "Orlando FL",
    "Sanford FL",
    "Clermont FL",
    "Leesburg FL",
    "Ocala FL",
    "Bradenton FL",
    "Sarasota FL",
    # === RING 4: Extended (75-100 mi) ===
    "Daytona Beach FL",
    "Melbourne FL",
    "Fort Myers FL",
    "Naples FL",
    "Gainesville FL",
    "The Villages FL",
]

# How many search combos to run per cycle (300 = ~10 min runtime)
SEARCHES_PER_CYCLE = 300
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
            "lead_source": "google_places",
            "raw_research": json.dumps({
                "google_rating": lead.get("google_rating"),
                "google_reviews": lead.get("google_reviews"),
                "email_source": lead.get("email_source", ""),
                "place_id": lead.get("place_id", ""),
                "location": lead.get("location", ""),
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
    google_key = os.environ.get("GOOGLE_PLACES_API_KEY", "")
    if not google_key or google_key == "AIzaSyALaxJstr7hiyyC52zTZOd2ymow5v1-PKY":
        # Fallback: Dan's Places-enabled key (Jan 2026)
        google_key = "AIzaSyDVL4vfogtIKRLqOFNPMcKOg1LEAb9dipc"
    hunter_key = os.environ.get("HUNTER_API_KEY", "")
    
    # Debug: show which key is being used
    print(f"🔑 Google Places key: {google_key[:12]}...")

    # Build search matrix
    search_combos = [(niche, city) for city in CITIES for niche in NICHES]
    total_combos = len(search_combos)
    print(f"📊 Search matrix: {len(NICHES)} niches × {len(CITIES)} cities = {total_combos} combos")

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
        supabase.table("system_health_log").insert({
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
