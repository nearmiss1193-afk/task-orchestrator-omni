"""
Part 3: Enrich SCRAPED_ leads with real GHL Contact IDs.
Board-approved: Use GHL Contacts API to bulk create contacts.
Batch at 2/sec to respect API rate limits.
"""
import os
import time
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
s = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

GHL_API_TOKEN = os.environ.get('GHL_AGENCY_API_TOKEN') or os.environ.get('GHL_API_TOKEN', '')
GHL_LOCATION_ID = "uFYcZA7Zk6EcBze5B4oH"
GHL_CONTACTS_URL = "https://services.leadconnectorhq.com/contacts/"

if not GHL_API_TOKEN:
    print("❌ CRITICAL: No GHL API token found!")
    exit(1)

print(f"GHL Token: {GHL_API_TOKEN[:15]}...")
print(f"GHL Location: {GHL_LOCATION_ID}")

# Get all SCRAPED_ leads
all_leads = s.table("contacts_master").select("id,full_name,email,phone,company_name,niche,ghl_contact_id").execute()
scraped_leads = [l for l in all_leads.data if (l.get('ghl_contact_id') or '').startswith('SCRAPED_')]

print(f"\nFound {len(scraped_leads)} SCRAPED_ leads to enrich")
print(f"Rate: 2 contacts/sec (to respect API limits)")
print(f"ETA: ~{len(scraped_leads) // 2} seconds ({len(scraped_leads) // 2 // 60} minutes)")

created = 0
failed = 0
skipped = 0

for i, lead in enumerate(scraped_leads):
    lead_id = lead['id']
    email = lead.get('email', '')
    phone = lead.get('phone', '')
    name = lead.get('full_name', '')
    company = lead.get('company_name', '')
    
    if not email and not phone:
        print(f"  [{i+1}/{len(scraped_leads)}] SKIP {name}: no email or phone")
        skipped += 1
        continue
    
    # Split name
    parts = name.split(' ', 1) if name else ['', '']
    first_name = parts[0] if parts else ''
    last_name = parts[1] if len(parts) > 1 else ''
    
    # Build GHL contact payload
    contact_data = {
        "locationId": GHL_LOCATION_ID,
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "phone": phone,
        "companyName": company,
        "source": "AI Prospecting",
        "tags": ["ai-prospected", "auto-enriched"]
    }
    
    # Remove empty fields
    contact_data = {k: v for k, v in contact_data.items() if v}
    contact_data["locationId"] = GHL_LOCATION_ID  # Always required
    
    try:
        headers = {
            "Authorization": f"Bearer {GHL_API_TOKEN}",
            "Content-Type": "application/json",
            "Version": "2021-07-28"
        }
        
        r = requests.post(GHL_CONTACTS_URL, headers=headers, json=contact_data, timeout=15)
        
        if r.status_code in [200, 201]:
            data = r.json()
            new_ghl_id = data.get('contact', {}).get('id', '')
            if new_ghl_id:
                # Update contacts_master with real GHL ID
                s.table("contacts_master").update({"ghl_contact_id": new_ghl_id}).eq("id", lead_id).execute()
                created += 1
                if created <= 5 or created % 50 == 0:
                    print(f"  [{i+1}/{len(scraped_leads)}] ✅ Created: {name} → {new_ghl_id[:15]}...")
            else:
                print(f"  [{i+1}/{len(scraped_leads)}] ⚠️ API OK but no ID: {data}")
                failed += 1
        elif r.status_code == 422:
            # Contact may already exist — check for duplicate
            resp_data = r.json()
            if 'contact already exists' in str(resp_data).lower() or 'duplicate' in str(resp_data).lower():
                # Try to extract existing contact ID
                existing_id = resp_data.get('contact', {}).get('id', '')
                if existing_id:
                    s.table("contacts_master").update({"ghl_contact_id": existing_id}).eq("id", lead_id).execute()
                    created += 1
                    print(f"  [{i+1}/{len(scraped_leads)}] ♻️ Existing: {name} → {existing_id[:15]}...")
                else:
                    print(f"  [{i+1}/{len(scraped_leads)}] ⚠️ Duplicate but no ID: {resp_data}")
                    failed += 1
            else:
                print(f"  [{i+1}/{len(scraped_leads)}] ❌ 422: {r.text[:100]}")
                failed += 1
        elif r.status_code == 429:
            print(f"  [{i+1}/{len(scraped_leads)}] 🛑 Rate limited! Waiting 10s...")
            time.sleep(10)
            failed += 1
        else:
            print(f"  [{i+1}/{len(scraped_leads)}] ❌ HTTP {r.status_code}: {r.text[:100]}")
            failed += 1
            
    except Exception as e:
        print(f"  [{i+1}/{len(scraped_leads)}] ❌ Error: {e}")
        failed += 1
    
    # Rate limit: 2/sec
    time.sleep(0.5)
    
    # Progress report every 50
    if (i + 1) % 50 == 0:
        print(f"\n--- Progress: {i+1}/{len(scraped_leads)} | Created: {created} | Failed: {failed} | Skipped: {skipped} ---\n")

print(f"\n{'='*50}")
print(f"ENRICHMENT COMPLETE")
print(f"  Created/Updated: {created}")
print(f"  Failed:          {failed}")
print(f"  Skipped:         {skipped}")
print(f"  Total processed: {created + failed + skipped}")
print(f"{'='*50}")
