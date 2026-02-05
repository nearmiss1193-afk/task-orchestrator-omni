"""
GHL Client - Shared GoHighLevel API connection for all Railway workers
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GHL_API_BASE = "https://services.leadconnectorhq.com"
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID", "uFYcZA7Zk6EcBze5B4oH")


def get_headers() -> dict:
    """Get GHL API headers with auth"""
    api_key = os.getenv("GHL_API_KEY")
    if not api_key:
        raise ValueError("GHL_API_KEY must be set")
    
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }


def create_contact(contact_data: dict) -> dict:
    """Create a contact in GHL"""
    url = f"{GHL_API_BASE}/contacts/"
    
    payload = {
        "locationId": GHL_LOCATION_ID,
        "firstName": contact_data.get("first_name", ""),
        "lastName": contact_data.get("last_name", ""),
        "email": contact_data.get("email"),
        "phone": contact_data.get("phone"),
        "companyName": contact_data.get("company_name", ""),
        "website": contact_data.get("website_url", ""),
        "source": "Railway Prospecting Engine",
        "tags": ["prospect", "railway-import"]
    }
    
    with httpx.Client(timeout=30) as client:
        response = client.post(url, headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


def add_contact_to_workflow(contact_id: str, workflow_id: str) -> dict:
    """Add a contact to a GHL workflow"""
    url = f"{GHL_API_BASE}/contacts/{contact_id}/workflow/{workflow_id}"
    
    with httpx.Client(timeout=30) as client:
        response = client.post(url, headers=get_headers(), json={})
        response.raise_for_status()
        return response.json()


def trigger_outreach_workflow(contact_id: str) -> dict:
    """Trigger the cold email workflow for a contact"""
    # Default workflow ID for cold email sequence
    workflow_id = os.getenv("GHL_OUTREACH_WORKFLOW_ID", "4d138ed0-d86e-49f2-b214-3f44e2657285")
    return add_contact_to_workflow(contact_id, workflow_id)


def send_email(contact_id: str, subject: str, body: str) -> dict:
    """Send a one-off email to a contact"""
    url = f"{GHL_API_BASE}/conversations/messages"
    
    payload = {
        "type": "Email",
        "contactId": contact_id,
        "subject": subject,
        "html": body
    }
    
    with httpx.Client(timeout=30) as client:
        response = client.post(url, headers=get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


def get_contact(contact_id: str) -> dict:
    """Get a contact by ID"""
    url = f"{GHL_API_BASE}/contacts/{contact_id}"
    
    with httpx.Client(timeout=30) as client:
        response = client.get(url, headers=get_headers())
        response.raise_for_status()
        return response.json()


def search_contacts(query: str, limit: int = 10) -> list:
    """Search for contacts by query"""
    url = f"{GHL_API_BASE}/contacts/"
    params = {
        "locationId": GHL_LOCATION_ID,
        "query": query,
        "limit": limit
    }
    
    with httpx.Client(timeout=30) as client:
        response = client.get(url, headers=get_headers(), params=params)
        response.raise_for_status()
        return response.json().get("contacts", [])


if __name__ == "__main__":
    # Quick test
    print("Testing GHL API connection...")
    try:
        contacts = search_contacts("test", limit=1)
        print(f"✅ GHL API working - found {len(contacts)} contacts")
    except Exception as e:
        print(f"❌ GHL API error: {e}")
