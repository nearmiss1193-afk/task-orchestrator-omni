"""
LEAD ENRICHMENT PIPELINE - Enrich leads before outreach
Runs BEFORE campaign to ensure leads have contact info
"""
import requests
import json
from datetime import datetime

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
GEMINI_API_KEY = "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo"


def get_leads_needing_enrichment(limit: int = 20) -> list:
    """Get leads that need enrichment (missing email or phone)"""
    # Get leads with status=new that are missing email
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=HEADERS,
        params={
            "status": "eq.new",
            "email": "is.null",
            "limit": limit
        }
    )
    leads_no_email = r.json() if r.status_code == 200 else []
    
    # Also get leads with no phone
    r2 = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=HEADERS,
        params={
            "status": "eq.new",
            "phone": "is.null",
            "limit": limit
        }
    )
    leads_no_phone = r2.json() if r2.status_code == 200 else []
    
    # Combine and deduplicate
    seen = set()
    result = []
    for lead in leads_no_email + leads_no_phone:
        if lead["id"] not in seen:
            seen.add(lead["id"])
            result.append(lead)
    
    return result[:limit]


def search_for_contact(company_name: str, city: str = "", industry: str = "") -> dict:
    """Use AI to search for company contact info"""
    prompt = f"""Find the decision maker email and phone for this company:
Company: {company_name}
City: {city}
Industry: {industry}

Search for:
1. Owner/Manager email (not info@ or contact@)
2. Direct phone number

Return ONLY valid JSON:
{{"email": "owner@company.com or null", "phone": "+1XXXXXXXXXX or null", "name": "Owner Name or null", "title": "Owner/Manager or null"}}

If you cannot find real info, return nulls. Do not make up data."""

    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        
        if r.status_code == 200:
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            # Clean JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
    except Exception as e:
        print(f"  [ERROR] Search failed: {e}")
    
    return {"email": None, "phone": None, "name": None, "title": None}


def enrich_lead(lead: dict) -> bool:
    """Enrich a single lead with contact info"""
    company = lead.get("company_name", "")
    city = lead.get("city", "")
    industry = lead.get("industry", "")
    
    print(f"  Enriching: {company}")
    
    contact = search_for_contact(company, city, industry)
    
    updates = {}
    if contact.get("email") and "@" in contact["email"]:
        updates["email"] = contact["email"]
    if contact.get("phone"):
        updates["phone"] = contact["phone"]
    if contact.get("name"):
        updates["contact_name"] = contact["name"]
    if contact.get("title"):
        updates["contact_title"] = contact["title"]
    
    if updates:
        updates["enriched_at"] = datetime.utcnow().isoformat() + "Z"
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}",
            headers=HEADERS,
            json=updates
        )
        print(f"    → Email: {updates.get('email', 'N/A')}, Phone: {updates.get('phone', 'N/A')}")
        return r.status_code in [200, 204]
    else:
        # Mark as enrichment failed - drop or flag
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}",
            headers=HEADERS,
            json={"enriched_at": datetime.utcnow().isoformat() + "Z", "enrichment_failed": True}
        )
        print(f"    → No contact info found")
        return False


def run_enrichment(limit: int = 10):
    """Run lead enrichment pipeline"""
    print("=" * 60)
    print(f"LEAD ENRICHMENT PIPELINE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    leads = get_leads_needing_enrichment(limit)
    print(f"\nFound {len(leads)} leads needing enrichment")
    
    enriched = 0
    failed = 0
    
    for lead in leads:
        if enrich_lead(lead):
            enriched += 1
        else:
            failed += 1
    
    print(f"\n[STATS] Enriched: {enriched}, No data found: {failed}")
    return {"enriched": enriched, "failed": failed}


if __name__ == "__main__":
    run_enrichment(limit=10)
