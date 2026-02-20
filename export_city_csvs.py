"""Export leads as region-labeled CSVs in batches of 500 to Desktop."""
import sys, os, csv, json, re
sys.path.insert(0, ".")
from dotenv import load_dotenv; load_dotenv()
from modules.database.supabase_client import get_supabase
from collections import defaultdict

sb = get_supabase()
DESKTOP = os.path.expanduser("~/Desktop/GHL_Lead_Lists")
os.makedirs(DESKTOP, exist_ok=True)
BATCH_SIZE = 2000
FIELDS = ["First Name", "Last Name", "Email", "Phone", "Company Name", "Tags", "Source"]

FL_MARKERS = {"FL", "Florida", "Lakeland", "Tampa", "Orlando", "Miami", "Jacksonville",
              "Clearwater", "Sarasota", "Bradenton", "Daytona", "Melbourne", "Naples",
              "Fort Myers", "Gainesville", "Ocala", "Kissimmee", "Winter Haven",
              "Bartow", "Sebring", "Brandon", "Riverview", "Plant City",
              "33801", "33803", "33805", "33809", "33810", "33811", "33812", "33813", "33815"}
MTN_MARKERS = {"CO", "AZ", "NV", "UT", "NM", "ID", "Denver", "Phoenix", "Scottsdale",
               "Mesa", "Tempe", "Tucson", "Las Vegas", "Henderson", "Salt Lake", "Boise",
               "Albuquerque", "Boulder", "Colorado Springs", "Reno"}
WC_MARKERS = {"CA", "OR", "WA", "Los Angeles", "San Diego", "San Francisco", "Oakland",
              "San Jose", "Portland", "Seattle", "Tacoma", "Sacramento", "Irvine",
              "Anaheim", "Riverside", "Long Beach", "Pasadena", "Bellevue", "Eugene", "Salem"}

def detect_region(row):
    ls = (row.get("lead_source", "") or "").lower()
    if "mountain" in ls: return "Mountain"
    if "west_coast" in ls: return "West_Coast"
    if "florida" in ls: return "Florida"
    
    try:
        rr = json.loads(row.get("raw_research", "{}") or "{}")
        if rr.get("region"):
            return rr["region"].replace("_", " ").title().replace(" ", "_")
        loc = rr.get("search_query", "") or rr.get("location", "") or ""
        for m in MTN_MARKERS:
            if m in loc: return "Mountain"
        for m in WC_MARKERS:
            if m in loc: return "West_Coast"
        for m in FL_MARKERS:
            if m in loc: return "Florida"
    except:
        pass
    return "Florida"

# Pull all leads
print("Pulling all leads...")
regions = defaultdict(list)
offset = 0
total = 0

while True:
    result = sb.table("contacts_master").select(
        "full_name,email,phone,company_name,niche,lead_source,raw_research"
    ).range(offset, offset + 999).execute()
    if not result.data: break
    
    for row in result.data:
        email = (row.get("email", "") or "").strip()
        phone = (row.get("phone", "") or "").strip()
        if not email and not phone: continue
        
        region = detect_region(row)
        full_name = (row.get("full_name", "") or "").strip()
        parts = full_name.split(" ", 1) if full_name else ["", ""]
        first = parts[0] if parts[0] and parts[0] != "Business" else "Business Owner"
        last = parts[1] if len(parts) > 1 else ""
        niche = (row.get("niche", "") or "general").replace(",", " ")
        
        regions[region].append({
            "First Name": first,
            "Last Name": last,
            "Email": email,
            "Phone": phone,
            "Company Name": row.get("company_name", "") or "",
            "Tags": f"prospector,{region.lower()},{niche}",
            "Source": "AI Service Co Prospector",
        })
        total += 1
    
    offset += 1000
    if len(result.data) < 1000: break

# Write CSVs in batches of 500
files = 0
for region, leads in sorted(regions.items(), key=lambda x: -len(x[1])):
    for i in range(0, len(leads), BATCH_SIZE):
        batch = leads[i:i + BATCH_SIZE]
        count = len(batch)
        part = (i // BATCH_SIZE) + 1
        total_parts = (len(leads) + BATCH_SIZE - 1) // BATCH_SIZE
        
        if total_parts > 1:
            fname = f"{region}_{count}_contacts_batch{part}of{total_parts}.csv"
        else:
            fname = f"{region}_{count}_contacts.csv"
        
        path = os.path.join(DESKTOP, fname)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(batch)
        files += 1
        print(f"  ✅ {fname}")

print(f"\n{'='*50}")
print(f"📂 {files} files → {DESKTOP}")
for r, l in sorted(regions.items(), key=lambda x: -len(x[1])):
    print(f"  {r}: {len(l)} contacts")
print(f"  TOTAL: {total}")
