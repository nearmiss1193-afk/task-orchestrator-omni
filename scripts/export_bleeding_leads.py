import os
import requests
import csv
import json
import sys
import io
from dotenv import load_dotenv

# Load local .env
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not SUPABASE_KEY:
    print("❌ ERROR: Set SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY in .env")
    exit(1)

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "count=exact"
}

def calculate_lead_score(lead: dict) -> int:
    """
    Calculates the 'Bleeding Lead' score (0-10).
    +3: Review count < 50 (Identity gap)
    +2: Rating < 4.5 (Reputation gap)
    +3: No website (Digital gap)
    +2: Tier 1 Vertical (High-stakes gap)
    """
    score = 0
    
    # Review Count Gap
    reviews = lead.get("google_reviews") or 0
    if reviews < 50:
        score += 3
    elif reviews < 100:
        score += 1
        
    # Rating Gap
    rating = lead.get("google_rating") or 5.0
    if rating < 4.5:
        score += 2
        
    # Digital Gap
    if not lead.get("website_url"):
        score += 3
        
    # Vertical Priority
    tier1 = ["tree", "gutter", "pool", "lawn", "hvac", "plumbing", "roofing"]
    name_low = (lead.get("company_name", "") or "").lower()
    if any(v in name_low for v in tier1):
        score += 2
        
    return min(score, 10)

def fetch_lakeland_leads():
    """Fetch all leads and filter in memory for max reliability"""
    all_leads = []
    offset = 0
    batch = 1000
    
    LAKELAND_ZIPS = ["33801", "33803", "33805", "33809", "33810", "33811", "33812", "33813", "33815"]
    
    while True:
        url = f"{SUPABASE_URL}/rest/v1/contacts_master"
        params = {
            "select": "*",
            "offset": offset,
            "limit": batch,
            "order": "created_at.desc"
        }
        
        resp = requests.get(url, headers=HEADERS, params=params)
        print(f"  Fetching batch {offset}... Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"ERROR: {resp.status_code} - {resp.text}")
            break
            
        data = resp.json()
        print(f"  Retrieved {len(data)} leads from Supabase.")
        if not data:
            break
            
        for lead in data:
            # DEBUG: Filter check
            biz_name = lead.get("company_name", "Unknown")
            raw = {}
            if lead.get("raw_research"):
                try:
                    raw = json.loads(lead["raw_research"])
                except: pass
            
            loc = (raw.get("location") or "").lower()
            src = (lead.get("lead_source") or "").lower()
            name = (lead.get("company_name") or "").lower()
            
            # Match any Lakeland/Polk indicators
            is_match = any(z in loc for z in LAKELAND_ZIPS) or \
                      any(z in src for z in LAKELAND_ZIPS) or \
                      "lakeland" in loc or "lakeland" in src or "lakeland" in name or \
                      "polk" in loc or "polk" in src
            
            # Print EXACT match info for debugging
            if "338" in src or "lakeland" in loc:
                print(f"    Possible match: {biz_name} | loc: {loc} | src: {src} | is_match: {is_match}")
                
            if is_match:
                # Add calculated score
                lead["google_rating"] = raw.get("google_rating") or 0
                lead["google_reviews"] = raw.get("google_reviews") or 0
                lead["lead_score"] = calculate_lead_score(lead)
                all_leads.append(lead)
        
        print(f"Checked {offset + len(data)}, found {len(all_leads)} matches...")
        if len(data) < batch or offset >= 5000:
            break
        offset += batch
        
    return all_leads

def write_ghl_csv(leads, output_path):
    # Sort by lead_score DESC
    leads.sort(key=lambda x: x.get("lead_score") or 0, reverse=True)
    
    contactable = [l for l in leads if l.get("phone") or l.get("email")]
    
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["First Name", "Last Name", "Email", "Phone", "Company Name", "Tags", "Website", "Source", "Vulnerability Score"])
        
        for lead in contactable:
            name = (lead.get("full_name") or "").strip()
            parts = name.split(" ", 1)
            first = parts[0] if parts else ""
            last = parts[1] if len(parts) > 1 else ""
            
            phone = (lead.get("phone") or "").replace("-","").replace("(","").replace(")","").replace(" ","")
            if phone and not phone.startswith("+"):
                phone = f"+1{phone}"
            
            score = lead.get("lead_score") or 0
            tags = ["import:bleeding_leads", f"score:{score}"]
            if score >= 8:
                tags.append("priority:high")
            if "lakeland" in (lead.get("location") or "").lower():
                tags.append("region:lakeland")
            
            w.writerow([
                first, last,
                lead.get("email") or "",
                phone,
                lead.get("company_name") or "",
                ", ".join(tags),
                lead.get("website_url") or "",
                lead.get("lead_source") or "lakeland_scrape",
                score
            ])
    
    return len(contactable)

if __name__ == "__main__":
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    output_path = os.path.join(desktop, "BLEEDING_LEADS_LAKELAND_UPLOAD.csv")
    
    print("\n🔥 LAKELAND BLEEDING LEADS ENGINE 🔥")
    print("-----------------------------------")
    print("Fetching Lakeland leads from Supabase...")
    leads = fetch_lakeland_leads()
    print(f"Total Lakeland leads found: {len(leads)}")
    
    if not leads:
        print("⚠️ No leads found matching strict Lakeland criteria. Exporting last 20 leads as fallback...")
        url = f"{SUPABASE_URL}/rest/v1/contacts_master"
        params = {"select": "*", "limit": 20, "order": "created_at.desc"}
        resp = requests.get(url, headers=HEADERS, params=params)
        leads = resp.json()
        for l in leads: l["lead_score"] = calculate_lead_score(l)
    
    if not leads:
        print("❌ CRITICAL: No leads found at all in Supabase.")
    else:
        count = write_ghl_csv(leads, output_path)
        print(f"\n✅ SUCCESS! {count} prioritized leads exported.")
        print(f"📍 Location: {output_path}")
        print("\nINSTRUCTIONS:")
        print("1. Go to GHL -> Contacts -> Import Contacts")
        print("2. Upload THIS file.")
        print("3. Map 'Vulnerability Score' to a custom field or just use the Tags.")
        print("4. Sarah is ready for SMS outreach once imported.")
