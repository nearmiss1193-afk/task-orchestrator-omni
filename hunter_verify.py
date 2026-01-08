"""
HUNTER.IO EMAIL VERIFICATION
=============================
Verify emails and find contacts using Hunter.io API.
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

HUNTER_API_KEY = os.getenv('HUNTER_API_KEY', '')
HUNTER_BASE_URL = "https://api.hunter.io/v2"


def verify_email(email: str) -> dict:
    """Verify if an email address is valid and deliverable"""
    
    if not HUNTER_API_KEY:
        return mock_verify(email)
    
    try:
        response = requests.get(
            f"{HUNTER_BASE_URL}/email-verifier",
            params={"email": email, "api_key": HUNTER_API_KEY}
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            return {
                "email": email,
                "status": data.get('status'),  # valid, invalid, accept_all, unknown
                "score": data.get('score'),
                "deliverable": data.get('status') == 'valid',
                "disposable": data.get('disposable'),
                "webmail": data.get('webmail'),
                "verified_at": datetime.now().isoformat()
            }
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


def find_email(first_name: str, last_name: str, domain: str) -> dict:
    """Find email for a person at a company"""
    
    if not HUNTER_API_KEY:
        return mock_find(first_name, last_name, domain)
    
    try:
        response = requests.get(
            f"{HUNTER_BASE_URL}/email-finder",
            params={
                "domain": domain,
                "first_name": first_name,
                "last_name": last_name,
                "api_key": HUNTER_API_KEY
            }
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            return {
                "email": data.get('email'),
                "confidence": data.get('score'),
                "first_name": first_name,
                "last_name": last_name,
                "domain": domain,
                "position": data.get('position'),
                "linkedin": data.get('linkedin'),
                "found_at": datetime.now().isoformat()
            }
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


def domain_search(domain: str, limit: int = 10) -> dict:
    """Find all emails associated with a domain"""
    
    if not HUNTER_API_KEY:
        return mock_domain_search(domain)
    
    try:
        response = requests.get(
            f"{HUNTER_BASE_URL}/domain-search",
            params={
                "domain": domain,
                "limit": limit,
                "api_key": HUNTER_API_KEY
            }
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            return {
                "domain": domain,
                "organization": data.get('organization'),
                "emails_found": len(data.get('emails', [])),
                "emails": [
                    {
                        "email": e.get('value'),
                        "type": e.get('type'),
                        "confidence": e.get('confidence'),
                        "first_name": e.get('first_name'),
                        "last_name": e.get('last_name'),
                        "position": e.get('position')
                    }
                    for e in data.get('emails', [])
                ]
            }
        return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}


def batch_verify(emails: list) -> list:
    """Verify multiple emails"""
    results = []
    for email in emails:
        result = verify_email(email)
        results.append(result)
    return results


def enrich_prospect(prospect: dict) -> dict:
    """Enrich a prospect with Hunter.io data"""
    
    domain = prospect.get('website', '').replace('https://', '').replace('http://', '').split('/')[0]
    
    if not domain:
        return {**prospect, "hunter_enriched": False}
    
    # Try domain search first
    domain_data = domain_search(domain, 5)
    
    if domain_data.get('emails'):
        # Find decision makers
        decision_makers = [
            e for e in domain_data['emails']
            if any(role in (e.get('position', '') or '').lower() 
                   for role in ['owner', 'ceo', 'president', 'manager', 'director'])
        ]
        
        enriched = {
            **prospect,
            "hunter_enriched": True,
            "organization": domain_data.get('organization'),
            "emails_found": domain_data.get('emails_found'),
            "decision_makers": decision_makers,
            "all_emails": domain_data['emails']
        }
        
        return enriched
    
    return {**prospect, "hunter_enriched": False, "emails_found": 0}


# Mock functions
def mock_verify(email: str) -> dict:
    return {
        "email": email,
        "status": "valid",
        "score": 85,
        "deliverable": True,
        "mock": True,
        "message": "Hunter.io not configured - add HUNTER_API_KEY to .env"
    }


def mock_find(first_name: str, last_name: str, domain: str) -> dict:
    return {
        "email": f"{first_name.lower()}.{last_name.lower()}@{domain}",
        "confidence": 75,
        "mock": True,
        "message": "Hunter.io not configured - add HUNTER_API_KEY to .env"
    }


def mock_domain_search(domain: str) -> dict:
    return {
        "domain": domain,
        "emails_found": 0,
        "emails": [],
        "mock": True,
        "message": "Hunter.io not configured - add HUNTER_API_KEY to .env"
    }


def get_api_status() -> dict:
    """Get Hunter.io API status"""
    return {
        "configured": bool(HUNTER_API_KEY),
        "api_key_prefix": HUNTER_API_KEY[:8] + "..." if HUNTER_API_KEY else "Not set"
    }


if __name__ == "__main__":
    print("Hunter.io Status:")
    print(json.dumps(get_api_status(), indent=2))
    
    # Test verification
    result = verify_email("test@example.com")
    print("\nEmail Verification:")
    print(json.dumps(result, indent=2))
