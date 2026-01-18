#!/usr/bin/env python3
"""Quick check of Vapi phones"""
import os, requests
from dotenv import load_dotenv
load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
r = requests.get("https://api.vapi.ai/phone-number", headers={"Authorization": f"Bearer {VAPI_KEY}"})
if r.ok:
    for p in r.json():
        num = p.get('number', 'N/A')
        aid = p.get('assistantId', 'NONE')
        sms = p.get('smsEnabled', False)
        print(f"{num} | Assistant: {aid[:12] if aid else 'NONE'} | SMS: {sms}")
else:
    print(f"Error: {r.status_code}")
