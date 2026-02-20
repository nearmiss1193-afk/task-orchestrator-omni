"""
Generate GHL Contact Import CSV — Direct Supabase REST API
Queries contacts_master with pagination (1000/batch) and writes complete CSV.
"""
import requests
import csv
import os

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
# Try env var first, otherwise prompt
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not SUPABASE_KEY:
    print("ERROR: Set SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY env var")
    print("Example: $env:SUPABASE_KEY='eyJ...'")
    exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "count=exact"
}

def fetch_all_contacts():
    all_leads = []
    offset = 0
    batch = 1000
    
    while True:
        params = {
            "select": "id,full_name,email,phone,company_name,niche,status,lead_source,website_url",
            "status": "in.(new,research_done,outreach_sent,sequence_complete)",
            "offset": offset,
            "limit": batch
        }
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/contacts_master",
            headers=HEADERS,
            params=params
        )
        
        if resp.status_code != 200:
            print(f"ERROR {resp.status_code}: {resp.text}")
            break
        
        data = resp.json()
        if not data:
            break
        
        all_leads.extend(data)
        print(f"  Fetched {len(all_leads)} so far...")
        
        if len(data) < batch:
            break
        offset += batch
    
    return all_leads

def write_csv(leads, output_path):
    contactable = [l for l in leads if l.get("phone") or l.get("email")]
    
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["First Name", "Last Name", "Email", "Phone", "Company Name", "Tags", "Website", "Source"])
        
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
                lead.get("website_url") or "",
                lead.get("lead_source") or "supabase"
            ])
    
    return len(contactable)

if __name__ == "__main__":
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    output_path = os.path.join(desktop, "ghl_contact_import.csv")
    
    print("Fetching all contacts from Supabase...")
    leads = fetch_all_contacts()
    print(f"Total leads fetched: {len(leads)}")
    
    count = write_csv(leads, output_path)
    print(f"\nDone! {count} contactable leads saved to:")
    print(f"  {output_path}")
