import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('GEMINI_API_KEY')

candidates = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "gemini-1.5-pro-001",
    "gemini-1.5-pro-002",
    "gemini-pro",
    "gemini-1.0-pro"
]

print("🔍 SCANNING GEMINI MODELS...")

for model in candidates:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
    try:
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        if res.status_code == 200:
            print(f"✅ FOUND MATCH: {model}")
            exit(0)
        else:
            print(f"❌ {model}: {res.status_code}")
    except:
        pass

print("⚠️ NO WORKING MODELS FOUND IN LIST.")
