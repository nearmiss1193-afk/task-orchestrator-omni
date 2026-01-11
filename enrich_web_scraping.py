"""
WEB SCRAPING ENRICHMENT - For Small Local Businesses
Uses Google search, company websites, and AI to find owner info
"""
import os
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID', '017576662512468239146:omuauf_lfve')  # Custom search engine
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

def google_search(query, num_results=5):
    """Search Google for company info"""
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_SEARCH_ENGINE_ID,
            'q': query,
            'num': num_results
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('items', [])
    except Exception as e:
        print(f"Google search error: {e}")
    return []

def scrape_website(url):
    """Scrape a website for contact info"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text
            text = soup.get_text()
            
            # Look for owner/CEO mentions
            owner_patterns = [
                r'owner[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)',
                r'CEO[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)',
                r'president[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)',
                r'founded by ([A-Z][a-z]+ [A-Z][a-z]+)',
            ]
            
            for pattern in owner_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return {'name': match.group(1), 'source': 'website'}
            
            # Look for email addresses
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Z|a-z]{2,}', text)
            if emails:
                # Prioritize owner/info/contact emails
                for email in emails:
                    if any(word in email.lower() for word in ['owner', 'ceo', 'president', 'info', 'contact']):
                        return {'email': email, 'source': 'website'}
    except:
        pass
    return None

def ai_research(company_name, city, state):
    """Use Claude AI to research owner info"""
    try:
        prompt = f"""Find the owner or CEO name for this company:
Company: {company_name}
Location: {city}, {state}

Search the web and return ONLY the owner's name in this exact format:
Name: [First Last]

If you cannot find the owner, respond with: UNKNOWN"""

        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            },
            json={
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 100,
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['content'][0]['text']
            
            if 'UNKNOWN' not in content:
                # Extract name
                match = re.search(r'Name:\s*([A-Z][a-z]+ [A-Z][a-z]+)', content)
                if match:
                    return {'name': match.group(1), 'source': 'ai_research'}
    except Exception as e:
        print(f"AI research error: {e}")
    return None

def enrich_with_web_scraping(company_name, city, state):
    """
    Main web scraping enrichment function
    Tries: Google search -> Website scraping -> AI research
    """
    print(f"\n🔍 Web Scraping: {company_name}")
    
    # Step 1: Google search for company website
    search_query = f"{company_name} {city} {state} owner CEO"
    print(f"  🔎 Googling: {search_query}")
    
    search_results = google_search(search_query)
    
    website_url = None
    for result in search_results:
        url = result.get('link', '')
        # Skip social media, directories
        if not any(skip in url for skip in ['facebook.com', 'yelp.com', 'yellowpages.com', 'linkedin.com']):
            website_url = url
            break
    
    if website_url:
        print(f"  🌐 Found website: {website_url}")
        
        # Step 2: Scrape website
        scraped = scrape_website(website_url)
        if scraped:
            print(f"  ✅ Found from website: {scraped}")
            return scraped
    
    # Step 3: AI research as fallback
    print(f"  🤖 Trying AI research...")
    ai_result = ai_research(company_name, city, state)
    
    if ai_result:
        print(f"  ✅ AI found: {ai_result}")
        return ai_result
    
    print(f"  ❌ No owner info found")
    return None

# Test function
if __name__ == '__main__':
    # Test with a sample company
    result = enrich_with_web_scraping(
        "JW Plumbing Heating Air",
        "Los Angeles",
        "CA"
    )
    
    if result:
        print(f"\n✅ SUCCESS!")
        print(f"Result: {result}")
    else:
        print(f"\n❌ FAILED")
