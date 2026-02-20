"""
Generate GHL Import CSV for Jacksonville leads only.
Dan can import this to GHL to sync contacts. Then export GHL CSV to match IDs.
"""
import sys, csv
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase

sb = get_supabase()

# Fetch all Jacksonville leads
print("Fetching Jacksonville leads...")
jax = sb.table("contacts_master").select("*").eq("lead_source", "manus_jacksonville").execute()
leads = jax.data or []
print(f"Total Jacksonville leads: {len(leads)}")

output = r"C:\Users\nearm\Desktop\jacksonville_ghl_import.csv"

with open(output, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["First Name", "Last Name", "Email", "Phone", "Company Name", "Tags", "Website", "Source"])
    
    count = 0
    for lead in leads:
        name = (lead.get("full_name") or "").strip()
        parts = name.split(" ", 1)
        first = parts[0] if parts else ""
        last = parts[1] if len(parts) > 1 else ""
        
        phone = (lead.get("phone") or "")
        
        tags = [f"import:supabase", f"status:{lead.get('status','new')}", f"niche:{lead.get('niche','')}"]
        
        w.writerow([
            first, last,
            lead.get("email") or "",
            phone,
            lead.get("company_name") or "",
            ", ".join(tags),
            lead.get("website_url") or "",
            "manus_jacksonville"
        ])
        count += 1

print(f"\nDone! {count} Jacksonville leads saved to:")
print(f"  {output}")
print(f"\nImport this to GHL, then export back with GHL contact IDs for sync.")
