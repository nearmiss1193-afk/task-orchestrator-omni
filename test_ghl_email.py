"""Test GHL Email Sending via the new Empire Sentinel token."""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_ghl_email():
    token = os.getenv("GHL_API_TOKEN")
    location_id = os.getenv("GHL_LOCATION_ID")
    
    print(f"[TEST] Token: {token[:12]}...{token[-4:]}")
    print(f"[TEST] Location: {location_id}")
    
    # Step 1: Search for owner contact
    search_url = f"https://services.leadconnectorhq.com/contacts/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }
    
    search_payload = {
        "locationId": location_id,
        "query": "owner@aiserviceco.com"
    }
    
    print("\n[STEP 1] Searching for owner contact...")
    resp = requests.post(search_url, headers=headers, json=search_payload)
    print(f"[RESULT] Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        contacts = data.get("contacts", [])
        if contacts:
            contact_id = contacts[0].get("id")
            print(f"[FOUND] Contact ID: {contact_id}")
            return send_test_email(token, contact_id)
        else:
            print("[INFO] No contact found. Creating one...")
            return create_and_email(token, location_id, headers)
    else:
        print(f"[ERROR] Search failed: {resp.text[:200]}")
        return False

def create_and_email(token, location_id, headers):
    # Create the owner contact
    create_url = "https://services.leadconnectorhq.com/contacts/"
    create_payload = {
        "locationId": location_id,
        "email": "owner@aiserviceco.com",
        "firstName": "Empire",
        "lastName": "Owner",
        "source": "Empire Sentinel"
    }
    
    print("\n[STEP 2] Creating owner contact...")
    resp = requests.post(create_url, headers=headers, json=create_payload)
    print(f"[RESULT] Status: {resp.status_code}")
    
    if resp.status_code in [200, 201]:
        contact_id = resp.json().get("contact", {}).get("id")
        print(f"[CREATED] Contact ID: {contact_id}")
        return send_test_email(token, contact_id)
    else:
        print(f"[ERROR] Create failed: {resp.text[:200]}")
        return False

def send_test_email(token, contact_id):
    # Send email via conversations endpoint
    email_url = "https://services.leadconnectorhq.com/conversations/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Version": "2021-07-28",
        "Content-Type": "application/json"
    }
    
    email_payload = {
        "type": "Email",
        "contactId": contact_id,
        "subject": "[TEST] Empire Sentinel GHL Integration",
        "html": "<h2>GHL Integration Test</h2><p>This email confirms the Empire Sentinel token is working correctly.</p><p><strong>Status:</strong> OPERATIONAL</p>"
    }
    
    print(f"\n[STEP 3] Sending test email to contact {contact_id}...")
    resp = requests.post(email_url, headers=headers, json=email_payload)
    print(f"[RESULT] Status: {resp.status_code}")
    
    if resp.status_code in [200, 201]:
        print("[SUCCESS] Email sent via GHL!")
        return True
    else:
        print(f"[ERROR] Email failed: {resp.text[:300]}")
        return False

if __name__ == "__main__":
    success = test_ghl_email()
    print(f"\n[FINAL] GHL Email Test: {'PASSED' if success else 'FAILED'}")
