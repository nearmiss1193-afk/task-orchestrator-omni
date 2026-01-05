
import requests
import json

URL = "http://localhost:8001/submit-lead"

lead = {
    "name": "Grandma Rose",
    "phone": "+13529368152",
    "budget": 4500,
    "care_needs": "Assisted Living, Help Bathing",
    "preferred_city": "Orlando",
    "email": "nearmiss1193@gmail.com"
}

try:
    print(f"📤 Submitting Lead: {lead['name']}...")
    res = requests.post(URL, json=lead)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.json()}")
    
    if res.status_code == 200:
        print("✅ Lead Submitted Successfully.")
    else:
        print("❌ Submission Failed.")
except Exception as e:
    print(f"❌ Connection Error: {e}")
