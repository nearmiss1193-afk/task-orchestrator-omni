import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('GEMINI_API_KEY')
# Trying the model name exactly as it likely appears
model = "gemini-1.5-flash"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

print(f"Testing URL: {url.replace(key, '***')}")

payload = {
    "contents": [{"parts": [{"text": "Hello"}]}]
}

try:
    res = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
    print(f"Status: {res.status_code}")
    print(f"Body: {res.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
