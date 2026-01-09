# prelaunch_check_v2.py - Simple ASCII output
import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

print("=" * 50)
print("PRE-LAUNCH VERIFICATION")
print("=" * 50)

results = []

# 1. Dashboard
print("\n[1] DASHBOARD")
try:
    r = requests.get("https://client-portal-one-phi.vercel.app", timeout=10)
    status = r.status_code == 200
    print(f"    {'PASS' if status else 'FAIL'}: Status {r.status_code}")
    results.append(status)
except Exception as e:
    print(f"    FAIL: {e}")
    results.append(False)

# 2. Vapi Webhook
print("\n[2] VAPI WEBHOOK (Modal)")
try:
    r = requests.get("https://nearmiss1193-afk--vapi-live.modal.run", timeout=10)
    status = r.status_code in [200, 405, 307]
    print(f"    {'PASS' if status else 'FAIL'}: Status {r.status_code}")
    results.append(status)
except Exception as e:
    print(f"    FAIL: {e}")
    results.append(False)

# 3. Supabase
print("\n[3] SUPABASE")
try:
    s = create_client(os.getenv("NEXT_PUBLIC_SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    leads = s.table('leads').select('status, agent_research').execute()
    
    hvac = sum(1 for l in leads.data if l.get('agent_research', {}).get('industry') == 'HVAC')
    roofing = sum(1 for l in leads.data if l.get('agent_research', {}).get('industry') == 'Roofing')
    ready = sum(1 for l in leads.data if l.get('status') == 'ready_to_send')
    
    print(f"    PASS: Connected")
    print(f"    - HVAC Leads: {hvac}")
    print(f"    - Roofing Leads: {roofing}")
    print(f"    - Ready to Call: {ready}")
    results.append(True)
except Exception as e:
    print(f"    FAIL: {e}")
    results.append(False)

# 4. Vapi Assistants
print("\n[4] VAPI ASSISTANTS")
VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
headers = {"Authorization": f"Bearer {VAPI_KEY}"}
try:
    r = requests.get("https://api.vapi.ai/assistant", headers=headers, timeout=10)
    assistants = r.json()
    sarah = next((a for a in assistants if 'Sarah' in a.get('name', '')), None)
    john = next((a for a in assistants if 'John' in a.get('name', '')), None)
    
    print(f"    Sarah: {'FOUND - ' + sarah.get('id')[:8] if sarah else 'NOT FOUND'}")
    print(f"    John:  {'FOUND - ' + john.get('id')[:8] if john else 'NOT FOUND'}")
    results.append(sarah is not None and john is not None)
except Exception as e:
    print(f"    FAIL: {e}")
    results.append(False)

# 5. Phone Numbers
print("\n[5] PHONE NUMBERS")
try:
    r = requests.get("https://api.vapi.ai/phone-number", headers=headers, timeout=10)
    phones = [p for p in r.json() if p.get('number')]
    for p in phones:
        print(f"    - {p.get('number')}: {p.get('name', 'Unnamed')}")
    results.append(len(phones) >= 2)
except Exception as e:
    print(f"    FAIL: {e}")
    results.append(False)

# 6. GHL Token
print("\n[6] GHL TOKEN")
ghl = bool(os.getenv("GHL_AGENCY_API_TOKEN"))
print(f"    {'PASS: Configured' if ghl else 'FAIL: Missing'}")
results.append(ghl)

# Summary
print("\n" + "=" * 50)
passed = sum(results)
total = len(results)
print(f"RESULT: {passed}/{total} checks passed")
print("STATUS: " + ("READY TO LAUNCH!" if passed >= 5 else "ISSUES FOUND"))
print("=" * 50)
