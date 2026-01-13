"""Quick status check"""
import requests
import os
from dotenv import load_dotenv
load_dotenv()

print("="*50)
print("SYSTEM STATUS CHECK")
print("="*50)

# Vapi Phone Numbers
print("\n📞 VAPI PHONE NUMBERS:")
key = os.getenv('VAPI_PRIVATE_KEY')
if key:
    try:
        r = requests.get('https://api.vapi.ai/phone-number', headers={'Authorization': f'Bearer {key}'}, timeout=10)
        if r.ok:
            phones = r.json()
            print(f"   Total: {len(phones)}")
            for p in phones:
                num = p.get('number', '?')
                sms = p.get('smsEnabled', False)
                assistant = p.get('assistantId', 'none')
                print(f"   {num} | SMS Enabled: {sms} | Assistant: {assistant[:12] if assistant else 'none'}...")
        else:
            print(f"   Error: {r.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

# Vapi Calls Today
print("\n📊 VAPI CALLS TODAY:")
try:
    r = requests.get('https://api.vapi.ai/call', headers={'Authorization': f'Bearer {key}'}, timeout=10)
    if r.ok:
        calls = r.json()
        today = [c for c in calls if '2026-01-13' in c.get('createdAt', '')]
        print(f"   Calls today: {len(today)}")
except Exception as e:
    print(f"   Error: {e}")

# Modal Cloud
print("\n☁️ MODAL CLOUD:")
print("   App: empire-webhooks")
print("   Health: https://nearmiss1193-afk--empire-webhooks-health.modal.run")

# Supabase
print("\n💾 SUPABASE:")
try:
    from supabase import create_client
    url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    skey = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    sb = create_client(url, skey)
    leads = sb.table('leads').select('*').execute()
    print(f"   Leads: {len(leads.data) if leads.data else 0}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*50)
