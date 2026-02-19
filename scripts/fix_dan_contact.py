"""Create Dan as a GHL contact + test notification"""
import os, requests, json
from dotenv import load_dotenv
load_dotenv(".env")

GHL_API_KEY = os.environ["GHL_API_KEY"]
GHL_LOCATION = "uFYcZA7Zk6EcBze5B4oH"

# 1. Create Dan as a GHL contact
headers = {
    "Authorization": f"Bearer {GHL_API_KEY}",
    "Content-Type": "application/json",
    "Version": "2021-07-28"
}

# First check if Dan already exists
search = requests.get(
    f"https://services.leadconnectorhq.com/contacts/search/duplicate",
    headers=headers,
    params={"locationId": GHL_LOCATION, "phone": "+13529368152"}
)
print(f"Search for Dan: {search.status_code} - {search.text[:200]}")

# Create Dan as contact
create_data = {
    "firstName": "Dan",
    "lastName": "Owner",
    "phone": "+13529368152",
    "email": "dan@aiserviceco.com",
    "locationId": GHL_LOCATION,
    "tags": ["owner", "internal"]
}

r1 = requests.post(
    "https://services.leadconnectorhq.com/contacts/",
    headers=headers,
    json=create_data
)
print(f"\nCreate Dan contact: {r1.status_code}")
print(r1.text[:300])

# 2. Now test the webhook
GHL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
r2 = requests.post(GHL_WEBHOOK, json={
    "phone": "+13529368152",
    "message": "TEST ALERT: Notifications are now working! You will get alerts for every call and chat to Sarah."
}, timeout=10)
print(f"\nWebhook test after contact creation: {r2.status_code} - {r2.text[:200]}")
