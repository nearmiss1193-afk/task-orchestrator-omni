# prelaunch_check.py - Full A-Z system verification
import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_item(name, status, detail=""):
    icon = "✅" if status else "❌"
    print(f"{icon} {name}" + (f" - {detail}" if detail else ""))
    return status

results = []
print("=" * 50)
print("PRE-LAUNCH VERIFICATION: A-Z")
print("=" * 50)

# 1. Dashboard/Website
print("\n--- WEBSITES ---")
try:
    r = requests.get("https://client-portal-one-phi.vercel.app", timeout=10)
    results.append(check_item("Dashboard (Vercel)", r.status_code == 200, f"Status: {r.status_code}"))
except Exception as e:
    results.append(check_item("Dashboard (Vercel)", False, str(e)))

# 2. Vapi Webhook
print("\n--- VAPI WEBHOOK ---")
try:
    r = requests.get("https://nearmiss1193-afk--vapi-live.modal.run", timeout=10)
    results.append(check_item("Vapi Webhook (Modal)", r.status_code in [200, 405], f"Status: {r.status_code}"))
except Exception as e:
    results.append(check_item("Vapi Webhook (Modal)", False, str(e)))

# 3. Health Endpoint
print("\n--- MODAL HEALTH ---")
try:
    r = requests.get("https://nearmiss1193-afk--health-live.modal.run", timeout=10)
    results.append(check_item("Health Endpoint", r.status_code == 200, f"Status: {r.status_code}"))
except Exception as e:
    results.append(check_item("Health Endpoint", False, str(e)))

# 4. Supabase
print("\n--- SUPABASE ---")
try:
    SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    s = create_client(SUPABASE_URL, SUPABASE_KEY)
    leads = s.table('leads').select('id').limit(1).execute()
    results.append(check_item("Supabase Connection", True, "Connected"))
    
    # Count leads
    all_leads = s.table('leads').select('status, agent_research').execute()
    hvac = sum(1 for l in all_leads.data if l.get('agent_research', {}).get('industry') == 'HVAC')
    roofing = sum(1 for l in all_leads.data if l.get('agent_research', {}).get('industry') == 'Roofing')
    print(f"   HVAC Leads: {hvac}")
    print(f"   Roofing Leads: {roofing}")
    print(f"   Total: {len(all_leads.data)}")
except Exception as e:
    results.append(check_item("Supabase Connection", False, str(e)))

# 5. Vapi Assistants
print("\n--- VAPI ASSISTANTS ---")
VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
headers = {"Authorization": f"Bearer {VAPI_KEY}"}

try:
    r = requests.get("https://api.vapi.ai/assistant", headers=headers, timeout=10)
    if r.status_code == 200:
        assistants = r.json()
        sarah = next((a for a in assistants if 'Sarah' in a.get('name', '')), None)
        john = next((a for a in assistants if 'John' in a.get('name', '')), None)
        
        results.append(check_item("Sarah Assistant", sarah is not None, sarah.get('name') if sarah else "Not found"))
        results.append(check_item("John Assistant", john is not None, john.get('name') if john else "Not found"))
        
        if john:
            print(f"   John ID: {john.get('id')}")
except Exception as e:
    results.append(check_item("Vapi Assistants", False, str(e)))

# 6. Phone Numbers
print("\n--- PHONE NUMBERS ---")
try:
    r = requests.get("https://api.vapi.ai/phone-number", headers=headers, timeout=10)
    if r.status_code == 200:
        phones = r.json()
        for p in phones:
            if p.get('number'):
                print(f"   {p.get('name', 'Unnamed')}: {p.get('number')}")
        results.append(check_item("Phone Numbers", len(phones) >= 2, f"{len(phones)} numbers configured"))
except Exception as e:
    results.append(check_item("Phone Numbers", False, str(e)))

# 7. GHL Token
print("\n--- GHL STATUS ---")
ghl_token = os.getenv("GHL_AGENCY_API_TOKEN")
results.append(check_item("GHL Token", bool(ghl_token), "Configured" if ghl_token else "Missing"))

# Summary
print("\n" + "=" * 50)
print("SUMMARY")
print("=" * 50)
passed = sum(1 for r in results if r)
total = len(results)
print(f"\nPassed: {passed}/{total}")
print(f"Status: {'READY TO LAUNCH' if passed == total else 'ISSUES FOUND'}")
