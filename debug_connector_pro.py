import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('GEMINI_API_KEY')
# Testing gemini-1.5-pro-latest
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={key}"

print(f"Testing URL: {url.split('?')[0]}...")

payload = {
    "contents": [{"parts": [{"text": "Reply with 'OK'."}]}]
}

try:
    res = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")
except Exception as e:
    print(f"Exception: {e}")
