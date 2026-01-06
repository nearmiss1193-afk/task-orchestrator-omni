#!/usr/bin/env python3
"""
VAPI DIAGNOSTIC - Check phone numbers, assistants, and test outbound call
"""
import requests
import os
import sys

# Read VAPI key from .env file
VAPI_KEY = None
try:
    with open('.env', 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if 'VAPI_PRIVATE_KEY' in line and '=' in line:
                parts = line.split('=', 1)
                if len(parts) == 2:
                    VAPI_KEY = parts[1].strip().strip('"').strip("'")
                    break
except Exception as e:
    print(f"Error reading .env: {e}")

if not VAPI_KEY:
    print("ERROR: No VAPI_PRIVATE_KEY found in .env")
    sys.exit(1)

print("=" * 50)
print("         VAPI DIAGNOSTIC REPORT")
print("=" * 50)
print(f"\nAPI Key: {VAPI_KEY[:15]}...")

headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

# 1. Check Phone Numbers
print("\n[1] PHONE NUMBERS")
print("-" * 30)
try:
    r = requests.get("https://api.vapi.ai/phone-number", headers=headers)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        phones = r.json()
        if phones:
            for p in phones:
                print(f"  ✅ {p.get('number', 'N/A')}")
                print(f"     ID: {p.get('id', 'N/A')}")
                print(f"     Provider: {p.get('provider', 'N/A')}")
        else:
            print("  ❌ NO PHONE NUMBERS CONFIGURED!")
            print("     → You need to add a phone number in Vapi Dashboard")
            print("     → Go to: https://vapi.ai/dashboard/phone-numbers")
    else:
        print(f"  Error: {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# 2. Check Assistants
print("\n[2] ASSISTANTS")
print("-" * 30)
try:
    r = requests.get("https://api.vapi.ai/assistant", headers=headers)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        assts = r.json()
        for a in assts:
            print(f"  • {a.get('name', 'Unnamed')}")
            print(f"    ID: {a.get('id', 'N/A')}")
            model = a.get('model', {})
            print(f"    Model: {model.get('model', 'N/A')}")
    else:
        print(f"  Error: {r.text[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# 3. Check Account/Usage
print("\n[3] ACCOUNT STATUS")
print("-" * 30)
try:
    # Try to get calls to check if API is working
    r = requests.get("https://api.vapi.ai/call?limit=1", headers=headers)
    print(f"API Status: {r.status_code}")
    if r.status_code == 200:
        print("  ✅ API Connection Working")
    else:
        print(f"  ❌ API Error: {r.text[:100]}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Outbound Call Requirements
print("\n[4] OUTBOUND CALL REQUIREMENTS")
print("-" * 30)
try:
    r = requests.get("https://api.vapi.ai/phone-number", headers=headers)
    phones = r.json() if r.status_code == 200 else []
    
    if phones:
        phone_id = phones[0].get('id')
        print(f"  ✅ Phone Number ID available: {phone_id[:20]}...")
        print(f"     Use this for outbound calls!")
    else:
        print("  ❌ MISSING: Phone Number")
        print("     → Cannot make outbound calls without a phone number")
        print("     → Add one at: https://vapi.ai/dashboard/phone-numbers")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 50)
print("                  DIAGNOSIS")
print("=" * 50)

# Final diagnosis
issues = []
can_call = True

try:
    r = requests.get("https://api.vapi.ai/phone-number", headers=headers)
    phones = r.json() if r.status_code == 200 else []
    if not phones:
        issues.append("No phone number configured in Vapi")
        can_call = False
except:
    issues.append("Could not check phone numbers")
    can_call = False

if can_call:
    print("\n✅ System CAN make outbound calls")
    print(f"   Phone ID to use: {phones[0].get('id')}")
else:
    print("\n❌ System CANNOT make outbound calls")
    for issue in issues:
        print(f"   • {issue}")
    print("\n   FIX: Go to https://vapi.ai/dashboard/phone-numbers")
    print("        and add a phone number (Twilio or Vapi)")
