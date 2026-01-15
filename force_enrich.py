"""Force enrich leads with phone numbers via Apollo"""
import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.LqmVBpO9p9KhqkrGjAXFJQiePuFbbP9XC5H4xDAC9b8"
APOLLO_KEY = os.getenv("APOLLO_API_KEY", "pF0tLNqdgvPwW_2P5-FbSg")

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

def enrich_lead(email, name=None):
    """Get phone from Apollo"""
    try:
        resp = requests.post(
            "https://api.apollo.io/v1/people/match",
            headers={"Content-Type": "application/json", "Cache-Control": "no-cache"},
            json={"api_key": APOLLO_KEY, "email": email, "reveal_personal_emails": True, "reveal_phone_number": True}
        )
        if resp.status_code == 200:
            data = resp.json().get("person", {})
            phone = data.get("phone_numbers", [{}])[0].get("sanitized_number") if data.get("phone_numbers") else None
            return phone
    except Exception as e:
        print(f"   Apollo error: {e}")
    return None

def main():
    # Get leads without phones
    result = sb.table("leads").select("id, name, email").is_("phone", "null").limit(20).execute()
    leads = result.data
    print(f"Found {len(leads)} leads without phone numbers")
    
    enriched = 0
    for lead in leads:
        email = lead.get("email")
        if not email:
            continue
        print(f"Enriching {lead.get('name', 'Unknown')} ({email})...")
        phone = enrich_lead(email, lead.get("name"))
        if phone:
            sb.table("leads").update({"phone": phone}).eq("id", lead["id"]).execute()
            print(f"   ✓ Got phone: {phone}")
            enriched += 1
        else:
            print(f"   ✗ No phone found")
    
    print(f"\n=== ENRICHED {enriched}/{len(leads)} LEADS ===")

if __name__ == "__main__":
    main()
