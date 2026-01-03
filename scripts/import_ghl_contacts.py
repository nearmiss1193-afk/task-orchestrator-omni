import os
import requests
import json

try:
    from supabase import create_client
except ImportError:
    print("Supabase client not installed.")

def import_ghl_contacts():
    """
    Import contacts from GHL to Supabase (One-Way Sync).
    Does NOT delete from GHL.
    """
    print("📦 Starting GHL -> Sovereign Migration...")
    
    # Config
    ghl_token = os.environ.get("GHL_AGENCY_API_TOKEN")
    ghl_loc = os.environ.get("GHL_LOCATION_ID")
    supa_url = os.environ.get("SUPABASE_URL")
    supa_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not (ghl_token and ghl_loc and supa_url):
        print("❌ Missing Credentials. Check .env")
        return

    supabase = create_client(supa_url, supa_key)
    
    headers = {
        'Authorization': f'Bearer {ghl_token}',
        'Version': '2021-07-28',
        'Location-Id': ghl_loc
    }
    
    # Fetch Contacts (Paginated - Simplified for MVP)
    url = "https://services.leadconnectorhq.com/contacts/"
    
    try:
        print("   Fetching from GHL...")
        res = requests.get(url, headers=headers)
        data = res.json()
        contacts = data.get('contacts', [])
        print(f"   Found {len(contacts)} contacts in GHL.")
        
        count = 0
        for c in contacts:
            payload = {
                "ghl_contact_id": c['id'],
                "full_name": c.get('name') or f"{c.get('firstName')} {c.get('lastName')}",
                "email": c.get('email'),
                "phone": c.get('phone'),
                "status": "imported"
            }
            
            # Upsert into Sovereign DB
            supabase.table("contacts_master").upsert(payload, on_conflict="ghl_contact_id").execute()
            count += 1
            
        print(f"✅ Migrated {count} contacts to Sovereign Database.")
        print("🛡️ GHL Status: Untouched (Backup Active).")
        
    except Exception as e:
        print(f"❌ Migration Error: {e}")

if __name__ == "__main__":
    import_ghl_contacts()
