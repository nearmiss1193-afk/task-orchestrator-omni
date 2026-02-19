"""
Export Supabase contacts_master to GHL-compatible CSV.
Uses REST API directly — works without Modal env vars.
"""
import requests
import csv
import os

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
# Service role key from Modal secrets (agency-vault)
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not SUPABASE_KEY:
    # Try to load from .env or prompt
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        for line in open(env_path):
            if line.startswith("SUPABASE_SERVICE_ROLE_KEY=") or line.startswith("SUPABASE_KEY="):
                SUPABASE_KEY = line.split("=", 1)[1].strip().strip('"')
                break

if not SUPABASE_KEY:
    print("ERROR: Set SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY env var")
    print("  export SUPABASE_SERVICE_ROLE_KEY='eyJ...'")
    exit(1)

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "count=exact"
}

print("Fetching contacts from Supabase REST API...")
all_leads = []
offset = 0
batch = 1000

while True:
    url = f"{SUPABASE_URL}/rest/v1/contacts_master?select=id,full_name,email,phone,company_name,niche,city,state,status,lead_source,website_url&status=in.(new,research_done,outreach_sent,sequence_complete)&offset={offset}&limit={batch}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"ERROR: {r.status_code} - {r.text[:200]}")
        break
    data = r.json()
    if not data:
        break
    all_leads.extend(data)
    print(f"  Fetched {len(all_leads)}...")
    if len(data) < batch:
        break
    offset += batch

print(f"\nTotal leads: {len(all_leads)}")

# Filter contactable
contactable = [l for l in all_leads if l.get("phone") or l.get("email")]
has_phone = sum(1 for l in contactable if l.get("phone"))
has_email = sum(1 for l in contactable if l.get("email"))
print(f"Contactable: {len(contactable)} (phone: {has_phone}, email: {has_email})")

# Write GHL CSV
output = os.path.join(os.path.dirname(__file__), "scripts", "ghl_contact_import.csv")

with open(output, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["First Name", "Last Name", "Email", "Phone", "Company Name", "Tags", "City", "State", "Website", "Source"])
    
    for lead in contactable:
        name = (lead.get("full_name") or "").strip()
        parts = name.split(" ", 1)
        first = parts[0] if parts else ""
        last = parts[1] if len(parts) > 1 else ""
        
        phone = (lead.get("phone") or "").replace("-","").replace("(","").replace(")","").replace(" ","")
        if phone and not phone.startswith("+"):
            phone = f"+1{phone}"
        
        tags = ["import:supabase"]
        if lead.get("status"):
            tags.append(f"status:{lead['status']}")
        if lead.get("niche"):
            tags.append(f"niche:{lead['niche']}")
        
        w.writerow([
            first, last,
            lead.get("email") or "",
            phone,
            lead.get("company_name") or "",
            ", ".join(tags),
            lead.get("city") or "",
            lead.get("state") or "",
            lead.get("website_url") or "",
            lead.get("lead_source") or "supabase"
        ])

print(f"\n✅ CSV: {output}")
print(f"   Rows: {len(contactable)}")
print(f"   Import in GHL: Contacts > Import > Upload CSV")
