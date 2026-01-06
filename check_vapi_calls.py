"""
VAPI CALL STATUS CHECK
======================
Check recent calls and get transcripts
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")

if not VAPI_KEY:
    print("❌ VAPI_PRIVATE_KEY not found")
    exit(1)

headers = {"Authorization": f"Bearer {VAPI_KEY}"}

# Get recent calls
print("📞 Fetching recent Vapi calls...")
res = requests.get("https://api.vapi.ai/call", headers=headers, timeout=15)

if res.status_code == 200:
    calls = res.json()
    print(f"\n=== {len(calls)} Recent Calls ===\n")
    
    for call in calls[:10]:
        customer = call.get("customer", {})
        phone = customer.get("number", "Unknown")
        name = customer.get("name", "")
        status = call.get("status", "unknown")
        duration = call.get("duration", 0)
        created = call.get("createdAt", "")[:19] if call.get("createdAt") else "N/A"
        transcript = call.get("transcript", "")
        
        print(f"📱 To: {phone} ({name})")
        print(f"   Status: {status} | Duration: {duration}s | Created: {created}")
        
        if transcript:
            print(f"   Transcript: {transcript[:150]}...")
        print()
else:
    print(f"❌ API Error: {res.status_code}")
