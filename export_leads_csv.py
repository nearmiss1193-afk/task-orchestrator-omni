"""Pull leads and export region-tagged CSVs for GHL import.
Classifies existing leads by city/state from raw_research + company location."""
import sys, os, csv, json, re
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()
from modules.database.supabase_client import get_supabase
from datetime import datetime, timezone

sb = get_supabase()

# State-based region classification
FL_STATES = {"FL", "Florida"}
MOUNTAIN_STATES = {"CO", "Colorado", "AZ", "Arizona", "NV", "Nevada", 
                   "UT", "Utah", "NM", "New Mexico", "ID", "Idaho"}
WEST_COAST_STATES = {"CA", "California", "OR", "Oregon", "WA", "Washington"}

def detect_region(row):
    """Detect region from lead_source, raw_research, or niche/city clues."""
    ls = (row.get("lead_source", "") or "").lower()
    if "mountain" in ls: return "mountain"
    if "west_coast" in ls: return "west_coast"
    if "florida" in ls: return "florida"
    
    # Try raw_research
    try:
        rr = json.loads(row.get("raw_research", "{}") or "{}")
        if rr.get("region"): return rr["region"]
        
        # Check search_query or location for state
        location = rr.get("location", "") or rr.get("search_query", "") or ""
        for st in MOUNTAIN_STATES:
            if st in location: return "mountain"
        for st in WEST_COAST_STATES:
            if st in location: return "west_coast"
        for st in FL_STATES:
            if st in location: return "florida"
    except:
        pass
    
    # Default: florida (existing leads are all FL)
    return "florida"

# GHL CSV fields
fields = ["First Name", "Last Name", "Email", "Phone", "Company Name", "Tags", "Source"]

regions = {"florida": [], "mountain": [], "west_coast": []}

# Pull all leads with email or phone  
offset = 0
batch = 1000
while True:
    result = sb.table("contacts_master").select(
        "full_name,email,phone,company_name,niche,lead_source,status,raw_research"
    ).range(offset, offset + batch - 1).execute()
    
    if not result.data:
        break
    
    for row in result.data:
        email = (row.get("email", "") or "").strip()
        phone = (row.get("phone", "") or "").strip()
        if not email and not phone:
            continue
        
        region = detect_region(row)
        if region not in regions:
            region = "florida"
        
        full_name = (row.get("full_name", "") or "").strip()
        parts = full_name.split(" ", 1) if full_name else ["", ""]
        first_name = parts[0] if len(parts) > 0 else ""
        last_name = parts[1] if len(parts) > 1 else ""
        
        niche = (row.get("niche", "") or "general").replace(",", " ")
        
        regions[region].append({
            "First Name": first_name or "Business Owner",
            "Last Name": last_name,
            "Email": email,
            "Phone": phone,
            "Company Name": row.get("company_name", "") or "",
            "Tags": f"prospector,{region},{niche}",
            "Source": "AI Service Co Prospector",
        })
    
    offset += batch
    if len(result.data) < batch:
        break

# Write CSVs
os.makedirs("scripts/ghl_imports", exist_ok=True)
total = 0
for region, leads in regions.items():
    if not leads:
        print(f"  ⏭️  {region}: 0 leads (Mountain/West Coast will populate on next prospector cycle)")
        continue
    filename = f"scripts/ghl_imports/leads_{region}_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(leads)
    total += len(leads)
    print(f"  ✅ {filename} — {len(leads)} leads")

print(f"\nTotal: {total} leads exported")
print(f"\nCSV files ready in scripts/ghl_imports/")
print("Import to GHL: Contacts → Import → Upload CSV → Map fields")
