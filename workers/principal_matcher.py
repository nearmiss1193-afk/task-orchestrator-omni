"""
PRINCIPAL MATCHER v1 — Sunbiz-Powered Owner Identification
Iterates through contacts_master, scrapes Sunbiz for principals/officers,
and flags "Husband & Wife" (same last name) teams as priority leads.
"""
import os
import sys
import json
import re
import time
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from core.image_config import image, VAULT
from core.apps import engine_app as app

if "/root" not in sys.path:
    sys.path.append("/root")

def identify_husband_wife_teams(principals: list) -> bool:
    """
    Checks if multiple principals share a last name.
    Input: List of dicts with 'name' and 'title'.
    """
    if not principals or len(principals) < 2:
        return False
        
    last_names = []
    for p in principals:
        name = p.get("name", "").strip().upper()
        if not name: continue
        
        # Simple last name extraction (assumes LAST, FIRST MIDDLE and variants)
        # Most Sunbiz records are: SMITH, JOHN A
        parts = name.split(",")
        if len(parts) > 0:
            last_names.append(parts[0].strip())
            
    # Check for duplicates in last names
    from collections import Counter
    counts = Counter(last_names)
    for name, count in counts.items():
        if count >= 2:
            return True
            
    return False

def search_sunbiz_by_name(company_name: str) -> str:
    """
    Attempts to find a Sunbiz detail URL by business name.
    """
    if not company_name:
        return ""
        
    query = company_name.upper().replace(" ", "%20")
    search_url = f"https://search.sunbiz.org/Inquiry/CorporationSearch/SearchResults/EntityName/{query}/Page1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        r = requests.get(search_url, headers=headers, timeout=15)
        if r.status_code != 200:
            return ""
            
        soup = BeautifulSoup(r.text, 'html.parser')
        # Look for the first link in the results table
        results = soup.find_all("a", href=re.compile(r"/Inquiry/CorporationSearch/SearchResultDetail/"))
        if results:
            detail_url = "https://search.sunbiz.org" + results[0]['href']
            return detail_url
    except Exception as e:
        print(f"⚠️ Sunbiz search error for {company_name}: {e}")
        
    return ""
    """Fetches the principal/officer list from a Sunbiz detail page."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        r = requests.get(source_url, headers=headers, timeout=30)
        if r.status_code != 200:
            return []
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Look for "Officer/Director Detail" section
        principals = []
        detail_sections = soup.find_all('div', class_='detailSection')
        
        target_section = None
        for section in detail_sections:
            header = section.find('span')
            if header and ("Officer/Director Detail" in header.text or "Principal Officer Detail" in header.text):
                target_section = section
                break
                
        if target_section:
            # Each principal is typically in a separate div/span block
            # This is fragile and depends on current Sunbiz layout
            items = target_section.find_all('span')
            current_title = None
            for item in items:
                text = item.get_text().strip()
                if not text: continue
                
                # Heuristic: Titles are usually short codes (P, VP, D, S, T)
                if len(text) <= 5 and text.isupper():
                    current_title = text
                elif current_title:
                    principals.append({"name": text, "title": current_title})
                    current_title = None # Reset
                    
        return principals
    except Exception as e:
        print(f"  ❌ Scrape failed for {source_url}: {e}")
        return []

def run_principal_matching_strike(limit=100):
    """Iterates through leads to find owners."""
    from modules.database.supabase_client import get_supabase
    supabase = get_supabase()
    count = 0
    
    # Target leads that haven't been matched yet
    res = supabase.table("contacts_master").select("id,company_name,raw_research").order("created_at", desc=True).limit(limit).execute()
    leads = []
    for r in res.data:
        raw = r.get("raw_research")
        if isinstance(raw, str):
            try: raw = json.loads(raw)
            except: raw = {}
        
        if not raw or not raw.get("extraction_ts"):
            leads.append(r)
            
    print(f"🕵️ OWNER EXTRACTION: Auditing {len(leads)} fresh leads (of {len(res.data)} pulled)...")
    
    for lead in leads:
        try:
            raw = lead.get("raw_research") or {}
            if isinstance(raw, str):
                try: raw = json.loads(raw)
                except: raw = {}
                
            source_url = raw.get("source_url")
            if not source_url:
                # TRY TO FIND IT VIA SEARCH
                print(f"  🔍 URL missing for {lead['company_name']}, searching Sunbiz...")
                source_url = search_sunbiz_by_name(lead['company_name'])
                if source_url:
                    raw["source_url"] = source_url
                else:
                    # If no URL, we can't do deep principal matching yet
                    continue
                
            print(f"  🔍 Checking {lead['company_name']} at {source_url}...")
            principals = scrape_sunbiz_principals(source_url)
            
            is_hw = identify_husband_wife_teams(principals)
            
            # Update lead
            raw_data = raw # Use the already parsed 'raw'
            raw_data["is_priority_owner"] = is_hw
            raw_data["principal_matches"] = principals
            raw_data["extraction_ts"] = datetime.now(timezone.utc).isoformat()
            
            update_data = {
                "raw_research": json.dumps(raw_data)
            }
            
            supabase.table("contacts_master").update(update_data).eq("id", lead["id"]).execute()
            count += 1
            
            if is_hw:
                print(f"    ⭐ FOUND HUSBAND/WIFE TEAM: {lead['company_name']}")
            
            # Politeness delay for Sunbiz
            time.sleep(3)
        except Exception as e:
            print(f"❌ ERROR processing {lead.get('company_name')}: {e}")
            import traceback
            traceback.print_exc()

    return count

if __name__ == "__main__":
    run_principal_matching_strike(limit=50)
