import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv('GROK_API_KEY')
url = "https://api.x.ai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {GROK_API_KEY}"
}

prompt = """
Act as a lead generation expert. Find 5 REAL **HVAC** companies in Tampa, FL.
CRITICAL RULES:
1. DO NOT use fictional numbers (555-xxxx).
2. Provide REAL public phone numbers.
3. Return valid JSON only.

JSON Format:
[
    {
        "company_name": "Name",
        "phone": "8135551234"
    }
]
"""

payload = {
    "messages": [
        {"role": "system", "content": "You are a helpful data assistant. Return only JSON."},
        {"role": "user", "content": prompt}
    ],
    "model": "grok-2-1212",
    "stream": False,
    "temperature": 0.7
}

print("sending request...")
try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Raw: {response.text}")
except Exception as e:
    print(f"Error: {e}")
