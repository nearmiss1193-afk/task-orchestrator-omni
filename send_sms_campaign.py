#!/usr/bin/env python3
"""
EMERGENCY: Send first SMS batch NOW via GHL
"""
import os
import requests
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

# Get 25 HVAC contacts
print("📋 Getting HVAC contacts from Supabase...")
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/contacts_master?limit=25",
    headers=headers
)

if r.ok:
    contacts = r.json()
    print(f"Found {len(contacts)} contacts\n")
    
    sent = 0
    for c in contacts[:25]:
        phone = c.get('phone')
        company = c.get('company', 'your company')
        
        if not phone:
            print(f"⚠️ No phone for {company}")
            continue
        
        # Clean phone
        phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not phone.startswith('+'):
            phone = f"+1{phone}" if len(phone) == 10 else f"+{phone}"
        
        # SMS message
        message = f"Hi! I have a free diagnostic report ready for {company}. It shows where you might be losing leads. Reply YES to get it, or STOP to opt out."
        
        print(f"📱 Sending to {phone} ({company})...")
        
        # Send via GHL
        try:
            sms_r = requests.post(GHL_SMS_WEBHOOK, json={
                "phone": phone,
                "message": message,
                "company": company
            }, timeout=30)
            
            if sms_r.status_code in [200, 201]:
                print(f"   ✅ Sent!")
                sent += 1
            else:
                print(f"   ❌ Failed: {sms_r.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n=== CAMPAIGN COMPLETE: {sent} SMS sent ===")
else:
    print(f"ERROR getting contacts: {r.status_code} - {r.text}")
