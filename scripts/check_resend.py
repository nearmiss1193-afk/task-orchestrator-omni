"""Check Resend domain status"""
import os
from dotenv import load_dotenv
load_dotenv()
import requests
import json

key = os.getenv("RESEND_API_KEY")
r = requests.get(
    "https://api.resend.com/domains",
    headers={"Authorization": f"Bearer {key}"}
)
data = r.json()
for d in data.get("data", []):
    print(f"{d['name']}: {d['status']}")
