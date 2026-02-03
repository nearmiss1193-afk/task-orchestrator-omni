import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

GHL_API_TOKEN = os.getenv("GHL_API_TOKEN")
GHL_LOCATION_ID = os.getenv("GHL_LOCATION_ID")

def push_user_test_contact():
    """Pushes the user's specific contact details to GHL for testing."""
    
    if not GHL_API_TOKEN or not GHL_LOCATION_ID:
        print("Error: GHL_API_TOKEN or GHL_LOCATION_ID not found in .env.local")
        return

    url = "https://services.leadconnectorhq.com/contacts/"
    
    headers = {
        "Authorization": f"Bearer {GHL_API_TOKEN}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }

    # User's information as requested
    payload = {
        "firstName": "Dan",
        "lastName": "C",
        "email": "danc@freeplumberai.com",
        "phone": "+13529368152",
        "locationId": GHL_LOCATION_ID,
        "tags": ["trigger-vortex", "spartan-strike", "user-verification"],
        "customFields": [
            {"id": "annual_loss_projection", "value": "$144,000"},
            {"id": "vortex_audit_link", "value": "https://freeplumberai.com/vortex-audit-dan"}
        ]
    }

    try:
        print(f"Pushing user contact: {payload['email']}...")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            print("Successfully pushed user contact to GHL.")
            print(f"Response: {response.json()}")
        else:
            print(f"Error pushing user contact: {response.status_code}")
            print(f"Response Body: {response.text}")
            
    except Exception as e:
        print(f"Exception occurred during GHL push: {e}")

if __name__ == "__main__":
    push_user_test_contact()
