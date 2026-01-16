import requests
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}")
if r.ok:
    models = r.json().get("models", [])
    for m in models:
        print(f"MODEL: {m['name']}")
else:
    print(f"FAIL: {r.status_code} {r.text}")
