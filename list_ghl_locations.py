# list_ghl_locations.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GHL_AGENCY_API_TOKEN")

print(f"Token: {TOKEN[:10]}...")

url = "https://services.leadconnectorhq.com/locations/search?limit=10"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Version": "2021-07-28",
    "Accept": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        locations = data.get('locations', [])
        print(f"Found {len(locations)} locations:")
        for loc in locations:
            print(f"  - {loc.get('name')} (ID: {loc.get('id')})")
    else:
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
