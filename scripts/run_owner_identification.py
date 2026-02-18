"""
Owner Identification Engine — Local version
Scrapes Florida Sunbiz for principals/officers.
Flags leads where 2+ officers share a last name as 'husband & wife' teams.
These get is_priority_owner=True for SlyBroadcasting voice drops.

Rate limited to 3s between Sunbiz requests to avoid blocking.
"""
import os, sys, json, re, time
import requests
from datetime import datetime, timezone
from collections import Counter
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

from supabase import create_client

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

lines = []
def log(msg):
    lines.append(msg)
    print(msg, flush=True)

def identify_husband_wife_teams(principals):
    if not principals or len(principals) < 2:
        return False
    last_names = []
    for p in principals:
        name = p.get("name", "").strip().upper()
        if not name: continue
        parts = name.split(",")
        if parts:
            last_names.append(parts[0].strip())
    counts = Counter(last_names)
    for name, count in counts.items():
        if count >= 2:
            return True
    return False

def search_sunbiz(company_name):
    if not company_name:
        return ""
    query = company_name.upper().replace(" ", "%20")
    url = f"https://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults/EntityName/{query}/Page1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return ""
        soup = BeautifulSoup(r.text, 'html.parser')
        results = soup.find_all("a", href=re.compile(r"/Inquiry/CorporationSearch/SearchResultDetail/"))
        if results:
            return "https://search.sunbiz.org" + results[0]['href']
    except Exception as e:
        log(f"  Search error: {e}")
    return ""

def scrape_principals(detail_url):
    try:
        r = requests.get(detail_url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, 'html.parser')
        principals = []
        detail_sections = soup.find_all('div', class_='detailSection')
        
        target_section = None
        for section in detail_sections:
            header = section.find('span')
            if header and ("Officer/Director Detail" in header.text or "Principal" in header.text):
                target_section = section
                break
        
        if target_section:
            items = target_section.find_all('span')
            current_title = None
            for item in items:
                text = item.get_text().strip()
                if not text: continue
                if len(text) <= 5 and text.isupper() and text not in ["THE", "AND", "INC", "LLC", "FOR"]:
                    current_title = text
                elif current_title:
                    principals.append({"name": text, "title": current_title})
                    current_title = None
        return principals
    except Exception as e:
        log(f"  Scrape error: {e}")
        return []

def main():
    sb_url = os.environ["SUPABASE_URL"]
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_KEY"]
    sb = create_client(sb_url, sb_key)
    
    # Get lakeland_finds leads that haven't been processed yet
    log("OWNER IDENTIFICATION ENGINE - Starting")
    log("Fetching unprocessed lakeland_finds leads...")
    
    all_leads = []
    offset = 0
    while True:
        res = sb.table("contacts_master").select(
            "id,company_name,phone,raw_research"
        ).eq("source", "lakeland_finds").range(offset, offset + 499).execute()
        all_leads.extend(res.data)
        if len(res.data) < 500:
            break
        offset += 500
    
    log(f"Total lakeland_finds leads: {len(all_leads)}")
    
    # Filter to unprocessed
    unprocessed = []
    already_done = 0
    for lead in all_leads:
        raw = lead.get("raw_research")
        if isinstance(raw, str):
            try: raw = json.loads(raw)
            except: raw = {}
        if isinstance(raw, dict) and raw.get("extraction_ts"):
            already_done += 1
            continue
        unprocessed.append(lead)
    
    log(f"Already processed: {already_done}")
    log(f"To process: {len(unprocessed)}")
    
    if not unprocessed:
        log("Nothing to process!")
        save_results(0, 0, 0)
        return
    
    # Process in batches with rate limiting
    processed = 0
    found_hw = 0
    found_principals = 0
    errors = 0
    
    for lead in unprocessed:
        try:
            company = lead.get("company_name", "")
            if not company:
                continue
            
            # Search Sunbiz
            detail_url = search_sunbiz(company)
            time.sleep(2)  # Rate limit
            
            principals = []
            if detail_url:
                principals = scrape_principals(detail_url)
                time.sleep(1)  # Rate limit
            
            is_hw = identify_husband_wife_teams(principals)
            
            # Prepare raw_research update
            raw = lead.get("raw_research")
            if isinstance(raw, str):
                try: raw = json.loads(raw)
                except: raw = {}
            if not isinstance(raw, dict):
                raw = {}
            
            raw["is_priority_owner"] = is_hw
            raw["principal_matches"] = principals
            raw["extraction_ts"] = datetime.now(timezone.utc).isoformat()
            raw["sunbiz_url"] = detail_url
            
            sb.table("contacts_master").update(
                {"raw_research": json.dumps(raw)}
            ).eq("id", lead["id"]).execute()
            
            processed += 1
            if principals:
                found_principals += 1
            if is_hw:
                found_hw += 1
                log(f"  FOUND H/W TEAM: {company} ({len(principals)} principals)")
            
            if processed % 25 == 0:
                log(f"  Progress: {processed}/{len(unprocessed)} | H/W teams: {found_hw} | With principals: {found_principals}")
                
        except Exception as e:
            errors += 1
            if errors <= 5:
                log(f"  Error on {lead.get('company_name')}: {str(e)[:100]}")
    
    log(f"\nOWNER ID COMPLETE:")
    log(f"  Processed: {processed}")
    log(f"  Found principals: {found_principals}")
    log(f"  Husband/Wife teams: {found_hw}")
    log(f"  Errors: {errors}")
    
    save_results(processed, found_hw, errors)

def save_results(processed, found_hw, errors):
    result = f"OWNER ID RESULT: Processed {processed}, H/W teams found {found_hw}, Errors {errors}"
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "owner_id_result.txt"), 'w') as f:
        f.write(result + "\n")
        f.write("\n".join(lines))

if __name__ == "__main__":
    main()
