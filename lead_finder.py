"""
Improved Lead Finder - Yellow Pages + Direct Website Scraping
Works without any paid APIs - pure web scraping like Manus
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import sys

# Supabase config
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

# Rotate user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
]

# US cities with area codes
US_CITIES = [
    ("tampa-fl", "Tampa", "FL", "813"),
    ("orlando-fl", "Orlando", "FL", "407"),
    ("miami-fl", "Miami", "FL", "305"),
    ("jacksonville-fl", "Jacksonville", "FL", "904"),
    ("atlanta-ga", "Atlanta", "GA", "404"),
    ("houston-tx", "Houston", "TX", "713"),
    ("dallas-tx", "Dallas", "TX", "214"),
    ("phoenix-az", "Phoenix", "AZ", "602"),
    ("denver-co", "Denver", "CO", "303"),
    ("las-vegas-nv", "Las Vegas", "NV", "702"),
    ("charlotte-nc", "Charlotte", "NC", "704"),
    ("nashville-tn", "Nashville", "TN", "615"),
    ("austin-tx", "Austin", "TX", "512"),
    ("san-antonio-tx", "San Antonio", "TX", "210"),
    ("raleigh-nc", "Raleigh", "NC", "919")
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}

def extract_phone(text):
    """Extract US phone numbers"""
    patterns = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = match.group()
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 10:
                return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return None

def extract_email(text):
    """Extract email addresses"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    exclude = ['example', 'email.com', 'domain', 'your', 'test', 'sample']
    for email in matches:
        if not any(ex in email.lower() for ex in exclude):
            return email.lower()
    return None

def scrape_yellow_pages(city_slug, city_name, state, industry="hvac"):
    """Scrape Yellow Pages for local businesses"""
    leads = []
    url = f"https://www.yellowpages.com/{city_slug}/{industry}-contractors"
    
    print(f"  Scraping: {url}")
    
    try:
        resp = requests.get(url, headers=get_headers(), timeout=15)
        if resp.status_code != 200:
            print(f"    Status: {resp.status_code}")
            return leads
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find business result cards
        results = soup.find_all('div', {'class': 'result'})
        if not results:
            results = soup.find_all('div', {'class': 'v-card'})
        if not results:
            results = soup.find_all('div', {'class': 'info'})
        
        print(f"    Found {len(results)} results")
        
        for result in results[:5]:  # Limit to 5 per city
            try:
                # Get business name
                name_elem = result.find(['a', 'h2'], {'class': re.compile(r'business-name|name')})
                if not name_elem:
                    name_elem = result.find('a', href=True)
                
                name = name_elem.get_text(strip=True) if name_elem else None
                
                if not name or len(name) < 3:
                    continue
                
                # Get phone
                phone_elem = result.find(['div', 'span'], {'class': re.compile(r'phone')})
                phone = extract_phone(phone_elem.get_text()) if phone_elem else None
                if not phone:
                    phone = extract_phone(result.get_text())
                
                # Get website
                website = None
                for link in result.find_all('a', href=True):
                    href = link.get('href', '')
                    if 'website' in link.get_text().lower() or 'http' in href:
                        if href.startswith('http') and 'yellowpages' not in href:
                            website = href
                            break
                
                if name and (phone or website):
                    lead = {
                        "company_name": name[:100],
                        "phone": phone,
                        "website_url": website,
                        "city": city_name,
                        "state": state,
                        "industry": industry.upper(),
                        "status": "new"
                    }
                    
                    # Try to get email from website
                    if website:
                        email = scrape_website_for_email(website)
                        if email:
                            lead["email"] = email
                    
                    leads.append(lead)
                    print(f"    + {name[:40]} | {phone or 'no phone'}")
                    
            except Exception as e:
                continue
        
        return leads
    except Exception as e:
        print(f"    Error: {e}")
        return leads

def scrape_website_for_email(url):
    """Quick scrape for email"""
    try:
        resp = requests.get(url, headers=get_headers(), timeout=8)
        if resp.status_code == 200:
            email = extract_email(resp.text)
            if email:
                return email
            # Check contact page
            soup = BeautifulSoup(resp.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                if 'contact' in link.get('href', '').lower():
                    contact_url = link['href']
                    if not contact_url.startswith('http'):
                        contact_url = url.rstrip('/') + '/' + contact_url.lstrip('/')
                    try:
                        contact_resp = requests.get(contact_url, headers=get_headers(), timeout=5)
                        if contact_resp.status_code == 200:
                            return extract_email(contact_resp.text)
                    except:
                        pass
                    break
    except:
        pass
    return None

def save_lead(lead):
    """Save lead to Supabase"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    try:
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/leads",
            headers=headers,
            json=lead,
            timeout=15
        )
        return resp.status_code in [200, 201]
    except:
        return False

def find_leads(num_cities=3, industry="hvac"):
    """Find leads from Yellow Pages - no APIs needed"""
    print("=" * 60)
    print("MANUS-STYLE LEAD FINDER v2")
    print("Scraping Yellow Pages - No APIs Required")
    print("=" * 60)
    
    all_leads = []
    cities = random.sample(US_CITIES, min(num_cities, len(US_CITIES)))
    
    for city_slug, city_name, state, area_code in cities:
        print(f"\n[{city_name}, {state}]")
        
        leads = scrape_yellow_pages(city_slug, city_name, state, industry)
        
        for lead in leads:
            if save_lead(lead):
                all_leads.append(lead)
                print(f"      [SAVED]")
            else:
                print(f"      [SAVE FAILED]")
        
        # Rate limiting
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"IMPORTED {len(all_leads)} LEADS TO DATABASE")
    print("=" * 60)
    
    for lead in all_leads:
        print(f"  - {lead['company_name'][:35]} | {lead.get('phone', 'N/A')} | {lead['city']}, {lead['state']}")
    
    return all_leads

if __name__ == "__main__":
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    find_leads(num_cities=num)
