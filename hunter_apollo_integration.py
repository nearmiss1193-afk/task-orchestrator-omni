"""
hunter_apollo_integration.py
=============================
Email verification and contact enrichment via Hunter.io and Apollo.io APIs.

USAGE:
    from hunter_apollo_integration import verify_email, find_person_by_company

    # Verify an email
    result = verify_email("john@example.com")
    print(result)  # {'status': 'valid', 'score': 95, ...}

    # Find decision-makers at a company
    people = find_person_by_company("Acme Corp", "CEO")
    print(people)  # [{'name': 'John Smith', 'email': 'john@acme.com', ...}]

REQUIRED ENV VARS:
    HUNTER_API_KEY - Get from https://hunter.io/api_keys
    APOLLO_API_KEY - Get from https://app.apollo.io/#/settings/integrations/api
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY", "")

# ═══════════════════════════════════════════════════════════════════════════
# HUNTER.IO - Email Verification
# ═══════════════════════════════════════════════════════════════════════════

def verify_email(email):
    """
    Verify an email address using Hunter.io API.
    
    Args:
        email (str): The email address to verify.
    
    Returns:
        dict: Verification result with status, score, and details.
              status: 'valid', 'invalid', 'accept_all', 'webmail', 'disposable', 'unknown'
              score: 0-100 confidence score
    """
    if not HUNTER_API_KEY:
        return {
            "status": "error",
            "message": "HUNTER_API_KEY not set. Get one at https://hunter.io/api_keys"
        }
    
    url = "https://api.hunter.io/v2/email-verifier"
    params = {
        "email": email,
        "api_key": HUNTER_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and "data" in data:
            result = data["data"]
            return {
                "status": result.get("status", "unknown"),
                "score": result.get("score", 0),
                "email": result.get("email", email),
                "regexp": result.get("regexp", False),
                "gibberish": result.get("gibberish", False),
                "disposable": result.get("disposable", False),
                "webmail": result.get("webmail", False),
                "mx_records": result.get("mx_records", False),
                "smtp_server": result.get("smtp_server", False),
                "smtp_check": result.get("smtp_check", False),
                "accept_all": result.get("accept_all", False),
                "block": result.get("block", False),
                "sources": result.get("sources", [])
            }
        else:
            return {
                "status": "error",
                "message": data.get("errors", [{"details": "Unknown error"}])[0].get("details", "Unknown error")
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def find_email_by_domain(domain, first_name=None, last_name=None):
    """
    Find email address for a person at a domain using Hunter.io.
    
    Args:
        domain (str): Company domain (e.g., 'acme.com')
        first_name (str): Person's first name
        last_name (str): Person's last name
    
    Returns:
        dict: Found email and confidence score.
    """
    if not HUNTER_API_KEY:
        return {"status": "error", "message": "HUNTER_API_KEY not set"}
    
    url = "https://api.hunter.io/v2/email-finder"
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY
    }
    
    if first_name:
        params["first_name"] = first_name
    if last_name:
        params["last_name"] = last_name
    
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and "data" in data:
            result = data["data"]
            return {
                "email": result.get("email"),
                "score": result.get("score", 0),
                "first_name": result.get("first_name"),
                "last_name": result.get("last_name"),
                "position": result.get("position"),
                "company": result.get("company"),
                "domain": result.get("domain")
            }
        else:
            return {"status": "error", "message": "Email not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# APOLLO.IO - People/Company Search
# ═══════════════════════════════════════════════════════════════════════════

def find_person_by_company(company_name, title_keywords=None, limit=5):
    """
    Find decision-makers at a company using Apollo.io API.
    
    Args:
        company_name (str): Name of the company.
        title_keywords (str): Keywords to filter by title (e.g., 'CEO', 'Owner', 'VP')
        limit (int): Maximum number of results to return.
    
    Returns:
        list: List of people with name, email, title, company info.
    """
    if not APOLLO_API_KEY:
        return [{
            "status": "error",
            "message": "APOLLO_API_KEY not set. Get one at https://app.apollo.io/#/settings/integrations/api"
        }]
    
    url = "https://api.apollo.io/v1/mixed_people/search"
    
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": APOLLO_API_KEY
    }
    
    payload = {
        "q_organization_name": company_name,
        "page": 1,
        "per_page": limit
    }
    
    if title_keywords:
        payload["person_titles"] = [title_keywords]
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and "people" in data:
            people = []
            for person in data.get("people", []):
                people.append({
                    "name": person.get("name"),
                    "first_name": person.get("first_name"),
                    "last_name": person.get("last_name"),
                    "email": person.get("email"),
                    "title": person.get("title"),
                    "linkedin_url": person.get("linkedin_url"),
                    "phone": person.get("phone_numbers", [{}])[0].get("raw_number") if person.get("phone_numbers") else None,
                    "company": person.get("organization", {}).get("name"),
                    "company_domain": person.get("organization", {}).get("primary_domain"),
                    "city": person.get("city"),
                    "state": person.get("state")
                })
            return people
        else:
            return [{
                "status": "error",
                "message": data.get("message", "Unknown error")
            }]
    except Exception as e:
        return [{"status": "error", "message": str(e)}]


def enrich_contact(email):
    """
    Enrich a contact by email using Apollo.io.
    
    Args:
        email (str): Email address to enrich.
    
    Returns:
        dict: Enriched contact info.
    """
    if not APOLLO_API_KEY:
        return {"status": "error", "message": "APOLLO_API_KEY not set"}
    
    url = "https://api.apollo.io/v1/people/match"
    
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": APOLLO_API_KEY
    }
    
    payload = {
        "email": email
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and "person" in data:
            person = data["person"]
            return {
                "name": person.get("name"),
                "title": person.get("title"),
                "email": person.get("email"),
                "phone": person.get("phone_numbers", [{}])[0].get("raw_number") if person.get("phone_numbers") else None,
                "linkedin_url": person.get("linkedin_url"),
                "company": person.get("organization", {}).get("name"),
                "company_domain": person.get("organization", {}).get("primary_domain"),
                "company_size": person.get("organization", {}).get("estimated_num_employees"),
                "industry": person.get("organization", {}).get("industry")
            }
        else:
            return {"status": "error", "message": "Contact not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ═══════════════════════════════════════════════════════════════════════════
# BATCH PROCESSING
# ═══════════════════════════════════════════════════════════════════════════

def verify_email_batch(emails):
    """
    Verify multiple emails. Note: Hunter.io has rate limits (free: 25/mo).
    
    Args:
        emails (list): List of email addresses.
    
    Returns:
        list: List of verification results.
    """
    results = []
    for email in emails:
        result = verify_email(email)
        result["original_email"] = email
        results.append(result)
    return results


def find_decision_makers(company_name, titles=["CEO", "Owner", "President", "VP"]):
    """
    Find key decision-makers at a company.
    
    Args:
        company_name (str): Name of the company.
        titles (list): List of title keywords to search for.
    
    Returns:
        list: Combined list of all matching people.
    """
    all_people = []
    for title in titles:
        people = find_person_by_company(company_name, title, limit=3)
        for person in people:
            if "status" not in person:  # Skip errors
                all_people.append(person)
    return all_people


# ═══════════════════════════════════════════════════════════════════════════
# TEST / DEMO
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🔍 Hunter.io + Apollo.io Integration Test")
    print("=" * 50)
    
    # Test Hunter.io
    print("\n1. HUNTER.IO - Email Verification")
    if HUNTER_API_KEY:
        result = verify_email("test@example.com")
        print(f"   Status: {result.get('status')}, Score: {result.get('score', 'N/A')}")
    else:
        print("   ⚠️ HUNTER_API_KEY not set. Add to .env to enable.")
    
    # Test Apollo.io
    print("\n2. APOLLO.IO - People Search")
    if APOLLO_API_KEY:
        people = find_person_by_company("Microsoft", "CEO", limit=2)
        for p in people:
            if "name" in p:
                print(f"   Found: {p['name']} - {p.get('title', 'N/A')}")
            else:
                print(f"   Error: {p.get('message', 'Unknown')}")
    else:
        print("   ⚠️ APOLLO_API_KEY not set. Add to .env to enable.")
    
    print("\n" + "=" * 50)
    print("To enable, add these to your .env file:")
    print("   HUNTER_API_KEY=your_hunter_key_here")
    print("   APOLLO_API_KEY=your_apollo_key_here")
