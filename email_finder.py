"""
Decision Maker Email Finder
Uses Grok API (or Gemini fallback) to find owner/manager emails for HVAC companies
Scrapes website + uses AI to identify decision maker contact info
"""
import os
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

load_dotenv()

# API Keys
XAI_API_KEY = os.getenv("XAI_API_KEY")  # For Grok
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo")

# Supabase
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def scrape_website_content(url):
    """Get readable text from website for AI analysis"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Remove script/style
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        text = soup.get_text(separator=" ", strip=True)
        
        # Also get contact page if exists
        for link in soup.find_all("a", href=True):
            href = link.get("href", "").lower()
            if "contact" in href or "about" in href:
                contact_url = href if href.startswith("http") else url.rstrip("/") + "/" + href.lstrip("/")
                try:
                    contact_resp = requests.get(contact_url, headers=HEADERS, timeout=10)
                    contact_soup = BeautifulSoup(contact_resp.text, "html.parser")
                    text += " " + contact_soup.get_text(separator=" ", strip=True)
                except:
                    pass
                break
        
        return text[:8000]  # Limit for AI context
    except Exception as e:
        return f"Error scraping: {e}"

def extract_emails_from_text(text):
    """Extract all email addresses"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = list(set(re.findall(pattern, text.lower())))
    # Filter out junk
    exclude = ['example', 'test', 'sample', 'your', 'email@', 'info@info', 'no-reply', 'noreply']
    return [e for e in emails if not any(ex in e for ex in exclude)]

def ai_find_decision_maker(company_name, website_text, found_emails):
    """Use AI to identify the decision maker email"""
    
    prompt = f"""You are analyzing an HVAC company website to find the decision maker's email.

Company: {company_name}

Website Text (excerpt):
{website_text[:3000]}

Emails found on website: {found_emails}

TASK: Identify which email most likely belongs to the owner, founder, general manager, or key decision maker.

Rules:
1. Prefer emails with names (john@, mike@, sarah@) over generic (info@, contact@, support@)
2. Look for context clues like "Owner", "Founder", "President", "GM", "General Manager"
3. If only generic emails exist, return the most likely one for business inquiries
4. If you can guess a decision maker name from the text, try to construct their likely email

Return ONLY the best email address, nothing else. If you cannot find any suitable email, return "NOT_FOUND".
"""
    
    # Try Grok first, then Gemini
    if XAI_API_KEY:
        return call_grok(prompt)
    else:
        return call_gemini(prompt)

def call_grok(prompt):
    """Call Grok API (OpenAI-compatible)"""
    try:
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "grok-beta",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100
            },
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  Grok error: {e}")
    return None

def call_gemini(prompt):
    """Call Gemini API as fallback"""
    try:
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"  Gemini error: {e}")
    return None

def find_decision_maker_email(company_name, website_url):
    """Main function to find decision maker email for a company"""
    print(f"\n[FIND] {company_name}")
    print(f"  Website: {website_url}")
    
    # Step 1: Scrape website
    website_text = scrape_website_content(website_url)
    
    # Step 2: Extract emails
    found_emails = extract_emails_from_text(website_text)
    print(f"  Found emails: {found_emails}")
    
    if not found_emails:
        print("  No emails found on website")
        return None
    
    # Step 3: Use AI to identify decision maker
    if len(found_emails) == 1:
        # Only one email, use it
        decision_maker_email = found_emails[0]
    else:
        # Multiple emails, use AI
        ai_result = ai_find_decision_maker(company_name, website_text, found_emails)
        if ai_result and ai_result != "NOT_FOUND" and "@" in ai_result:
            decision_maker_email = ai_result.lower().strip()
        else:
            # Fallback: prefer non-generic emails
            preferred = [e for e in found_emails if not any(g in e for g in ['info@', 'contact@', 'support@', 'sales@', 'service@'])]
            decision_maker_email = preferred[0] if preferred else found_emails[0]
    
    print(f"  Decision Maker Email: {decision_maker_email}")
    return decision_maker_email

def update_lead_with_email(lead_id, email):
    """Update lead in Supabase with found email"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}",
            headers=headers,
            json={"email": email},
            timeout=15
        )
        return resp.status_code in [200, 204]
    except:
        return False

def enrich_leads_without_emails():
    """Find and add decision maker emails for leads missing email"""
    print("=" * 60)
    print("DECISION MAKER EMAIL FINDER")
    print("=" * 60)
    
    # Get leads without emails but with websites
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=headers,
        params={
            "select": "id,company_name,website_url,email",
            "email": "is.null",
            "website_url": "not.is.null",
            "limit": 10
        },
        timeout=15
    )
    
    leads = resp.json()
    print(f"\nFound {len(leads)} leads without emails but with websites")
    
    enriched = 0
    for lead in leads:
        if not lead.get("website_url"):
            continue
            
        email = find_decision_maker_email(lead["company_name"], lead["website_url"])
        
        if email:
            if update_lead_with_email(lead["id"], email):
                print(f"  [UPDATED] {lead['company_name']} -> {email}")
                enriched += 1
            else:
                print(f"  [SAVE FAILED]")
    
    print("\n" + "=" * 60)
    print(f"ENRICHED {enriched} LEADS WITH DECISION MAKER EMAILS")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test with specific URL
        url = sys.argv[1]
        email = find_decision_maker_email("Test Company", url)
        print(f"\nResult: {email}")
    else:
        # Enrich leads in database
        enrich_leads_without_emails()
