"""
Lead Finder - Manus-Style Web Scraping
Finds HVAC businesses without paid APIs (Apollo, etc.)
Uses Google Search + website scraping to extract contact info
"""
import requests
from bs4 import BeautifulSoup
import re
import time
import random

# Supabase config
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

# User agent for requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# US cities to search
US_CITIES = [
    ("Tampa", "FL"),
    ("Orlando", "FL"),
    ("Jacksonville", "FL"),
    ("Miami", "FL"),
    ("Atlanta", "GA"),
    ("Charlotte", "NC"),
    ("Houston", "TX"),
    ("Dallas", "TX"),
    ("San Antonio", "TX"),
    ("Phoenix", "AZ"),
    ("Denver", "CO"),
    ("Nashville", "TN"),
    ("Austin", "TX"),
    ("Raleigh", "NC"),
    ("Las Vegas", "NV")
]

def extract_email(text):
    """Extract email from text"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    # Filter out common non-business emails
    exclude = ['example.com', 'email.com', 'yourcompany', 'domain.com']
    for email in matches:
        if not any(ex in email.lower() for ex in exclude):
            return email
    return None

def extract_phone(text):
    """Extract US phone number from text"""
    patterns = [
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',
        r'1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            phone = match.group()
            # Format as +1 (XXX) XXX-XXXX
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 10:
                return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits.startswith('1'):
                return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return None

def scrape_website(url):
    """Scrape a website for contact info"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None, None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text()
        
        email = extract_email(text)
        phone = extract_phone(text)
        
        # Also check contact page
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if 'contact' in href:
                contact_url = href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
                try:
                    contact_resp = requests.get(contact_url, headers=HEADERS, timeout=10)
                    if contact_resp.status_code == 200:
                        contact_soup = BeautifulSoup(contact_resp.text, 'html.parser')
                        contact_text = contact_soup.get_text()
                        if not email:
                            email = extract_email(contact_text)
                        if not phone:
                            phone = extract_phone(contact_text)
                except:
                    pass
                break
        
        return email, phone
    except Exception as e:
        print(f"    Scrape error: {e}")
        return None, None

def search_yelp(city, state, industry="hvac"):
    """Search Yelp for businesses (no API needed)"""
    leads = []
    url = f"https://www.yelp.com/search?find_desc={industry}&find_loc={city}%2C+{state}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"  Yelp returned {resp.status_code}")
            return leads
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find business cards
        for biz in soup.find_all('div', {'class': re.compile(r'businessName')}):
            name = biz.get_text(strip=True)
            if name:
                leads.append({
                    "company_name": name,
                    "city": city,
                    "state": state,
                    "industry": industry.upper(),
                    "status": "new"
                })
        
        return leads[:5]  # Limit to 5 per city
    except Exception as e:
        print(f"  Yelp error: {e}")
        return leads

def search_google_organic(city, state, industry="hvac"):
    """
    Search using Duck Duck Go (no API needed, no rate limits)
    Returns business names to research
    """
    leads = []
    query = f"{industry} companies in {city} {state}"
    url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return leads
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Extract result titles and URLs
        for result in soup.find_all('a', {'class': 'result__a'}):
            title = result.get_text(strip=True)
            href = result.get('href', '')
            
            # Filter for business-looking results
            if any(kw in title.lower() for kw in ['hvac', 'heating', 'cooling', 'air', 'climate']):
                if href and 'http' in href:
                    leads.append({
                        "company_name": title[:100],
                        "website_url": href,
                        "city": city,
                        "state": state,
                        "industry": industry.upper(),
                        "status": "new"
                    })
        
        return leads[:3]  # Limit per city
    except Exception as e:
        print(f"  Search error: {e}")
        return leads

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

def find_leads(num_cities=5):
    """Main function to find leads like Manus"""
    print("=" * 60)
    print("MANUS-STYLE LEAD FINDER")
    print("Finding HVAC businesses without Apollo")
    print("=" * 60)
    
    all_leads = []
    cities_to_search = random.sample(US_CITIES, min(num_cities, len(US_CITIES)))
    
    for city, state in cities_to_search:
        print(f"\nSearching {city}, {state}...")
        
        # Try DuckDuckGo first
        leads = search_google_organic(city, state, "hvac")
        
        for lead in leads:
            print(f"  Found: {lead['company_name'][:40]}")
            
            # Try to scrape contact info if we have URL
            if lead.get('website_url'):
                email, phone = scrape_website(lead['website_url'])
                if email:
                    lead['email'] = email
                    print(f"    Email: {email}")
                if phone:
                    lead['phone'] = phone
                    print(f"    Phone: {phone}")
            
            # Save to database
            if lead.get('email') or lead.get('phone'):
                if save_lead(lead):
                    print(f"    [SAVED]")
                    all_leads.append(lead)
                else:
                    print(f"    [SAVE FAILED]")
        
        # Rate limiting
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print(f"FOUND {len(all_leads)} LEADS WITH CONTACT INFO")
    print("=" * 60)
    
    return all_leads

if __name__ == "__main__":
    find_leads(num_cities=3)  # Start with 3 cities
