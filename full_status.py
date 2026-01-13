"""
FULL STATUS CHECK - For User Report
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

print("="*60)
print("📊 EMPIRE STATUS REPORT")
print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

# === VAPI CALLS ===
print("\n📞 VAPI CALL LOG:")
vapi_key = os.getenv('VAPI_PRIVATE_KEY')
if vapi_key:
    try:
        resp = requests.get('https://api.vapi.ai/call', headers={'Authorization': f'Bearer {vapi_key}'}, timeout=10)
        if resp.ok:
            calls = resp.json()
            print(f"   Total Calls Recorded: {len(calls)}")
            answered = len([c for c in calls if c.get('status') == 'ended'])
            print(f"   Answered/Completed: {answered}")
            print("\n   Last 5 Calls:")
            for c in calls[-5:]:
                status = c.get('status', '?')
                number = c.get('customer', {}).get('number', 'unknown')
                created = c.get('createdAt', '?')[:16] if c.get('createdAt') else '?'
                duration = c.get('duration', 0)
                print(f"     [{status}] {number} | {created} | {duration}s")
        else:
            print(f"   Vapi API Error: {resp.status_code}")
    except Exception as e:
        print(f"   Vapi Error: {e}")
else:
    print("   Missing VAPI_PRIVATE_KEY")

# === BRAIN LOG ===
print("\n" + "-"*60)
print("🧠 BRAIN LEARNING LOG:")
brain_path = "brain_log.json"
if os.path.exists(brain_path):
    try:
        with open(brain_path, 'r') as f:
            brain_log = json.load(f)
        print(f"   Total Entries: {len(brain_log)}")
        if brain_log:
            print("   Last 3 entries:")
            for entry in brain_log[-3:]:
                print(f"     - {entry.get('type', '?')} | {entry.get('timestamp', '?')[:16]}")
    except Exception as e:
        print(f"   Error reading brain log: {e}")
else:
    print("   brain_log.json NOT FOUND (no learning events recorded yet)")

# === STRATEGY CONFIG ===
print("\n" + "-"*60)
print("🎯 CURRENT STRATEGY:")
strat_path = "strategy_config.json"
if os.path.exists(strat_path):
    try:
        with open(strat_path, 'r') as f:
            strat = json.load(f)
        print(f"   Target Niche: {strat.get('target_niche', 'N/A')}")
        print(f"   Last Updated: {strat.get('updated_at', 'N/A')}")
    except Exception as e:
        print(f"   Error: {e}")
else:
    print("   strategy_config.json NOT FOUND (using defaults)")

# === SUPABASE LEADS ===
print("\n" + "-"*60)
print("📈 LEAD DATABASE:")
try:
    from supabase import create_client
    url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')
    
    if url and key:
        supabase = create_client(url, key)
        leads = supabase.table('leads').select('*').execute()
        total = len(leads.data) if leads.data else 0
        with_audit = len([l for l in (leads.data or []) if l.get('audit_link')])
        emailed = len([l for l in (leads.data or []) if l.get('email_sent')])
        
        print(f"   Total Prospects: {total}")
        print(f"   With Audit Link (Ready): {with_audit}")
        print(f"   Emails Sent: {emailed}")
        
        if leads.data:
            print("\n   Last 5 Prospects:")
            for l in (leads.data or [])[-5:]:
                name = l.get('company_name', '?')[:30]
                email = l.get('email', 'N/A')
                status = 'READY' if l.get('audit_link') else 'PENDING'
                print(f"     [{status}] {name} | {email}")
    else:
        print("   Missing Supabase credentials")
except Exception as e:
    print(f"   Supabase Error: {e}")

print("\n" + "="*60)
print("REPORT COMPLETE")
print("="*60)
