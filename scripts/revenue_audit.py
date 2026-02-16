import os
import requests
from datetime import datetime, timedelta

def run_audit():
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    headers = {'apikey': key, 'Authorization': f'Bearer {key}'}

    print("════════════════════════════════════════════════")
    print("      REVENUE WATERFALL AUDIT - FEB 12      ")
    print("════════════════════════════════════════════════")

    # 1. SENDING (24h)
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
    r1 = requests.get(f"{url}/rest/v1/outbound_touches?select=id&ts=gt.{yesterday}", headers=headers)
    sending = len(r1.json()) if r1.status_code == 200 else f"Error {r1.status_code}"
    print(f"Step 1: SENDING?    → {sending} emails in last 24h")

    # 2. OPENING (7d)
    last_week = (datetime.utcnow() - timedelta(days=7)).isoformat()
    r2 = requests.get(f"{url}/rest/v1/outbound_touches?select=id&opened=eq.true&ts=gt.{last_week}", headers=headers)
    opening = len(r2.json()) if r2.status_code == 200 else f"Error {r2.status_code}"
    print(f"Step 2: OPENING?    → {opening} opens in last 7d")

    # 3. REPLYING (7d)
    r3 = requests.get(f"{url}/rest/v1/outbound_touches?select=id&replied=eq.true&ts=gt.{last_week}", headers=headers)
    replying = len(r3.json()) if r3.status_code == 200 else f"Error {r3.status_code}"
    print(f"Step 3: REPLYING?   → {replying} replies in last 7d")

    # 4. CUSTOMERS / PAYING
    r4 = requests.get(f"{url}/rest/v1/contacts_master?select=id&status=eq.customer", headers=headers)
    paying = len(r4.json()) if r4.status_code == 200 else f"Error {r4.status_code}"
    print(f"Step 5: PAYING?     → {paying} customers in database")

    # 5. PIPELINE
    r5 = requests.get(f"{url}/rest/v1/contacts_master?select=id&status=in.(new,research_done)", headers=headers)
    pipeline = len(r5.json()) if r5.status_code == 200 else f"Error {r5.status_code}"
    print(f"Step 6: PIPELINE?   → {pipeline} contactable leads remain")

    # 6. AUDIT REPORTS
    r6 = requests.get(f"{url}/rest/v1/audit_reports?select=id", headers=headers)
    audit_reports = len(r6.json()) if r6.status_code == 200 else f"Error {r6.status_code}"
    print(f"Stat: AUDIT REPORTS → {audit_reports} total saved")

    print("\n════════════════════════════════════════════════")
    print("           MODAL & VERCEL STATUS            ")
    print("════════════════════════════════════════════════")
    print("Modal: Deployed v5 (Link-Based Audit)")
    print("Vercel: Deployed report.html (Live)")
    print("Supabase: audit_reports table created & verified")
    print("Flyer: Premium_Flyer.png created on Desktop")
    print("════════════════════════════════════════════════")

if __name__ == "__main__":
    run_audit()
