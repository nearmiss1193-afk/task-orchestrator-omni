"""
TURBO OUTREACH - Direct calls to enriched leads
Bypasses Modal scheduling to get calls moving NOW
"""

import os
import sys
import json
import requests
import re
from datetime import datetime

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Get credentials
VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_ID = os.getenv("VAPI_PHONE_NUMBER_ID")
SARAH_ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

def validate_phone(phone_str):
    """Validate phone - reject fakes"""
    if not phone_str:
        return False, None, "missing"
    cleaned = re.sub(r'\D', '', str(phone_str))
    if len(cleaned) < 10:
        return False, None, "too_short"
    exchange = cleaned[-7:-4] if len(cleaned) >= 7 else ""
    if exchange == "555":
        return False, None, "fake_555"
    return True, cleaned[-10:], None

def get_enriched_leads():
    """Fetch leads with valid enriched phones"""
    from supabase import create_client
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get leads that have NOT been called recently
    result = client.table("leads").select("*")\
        .in_("status", ["new", "processing_email", "enriched"])\
        .limit(10)\
        .execute()
    
    callable_leads = []
    for lead in result.data:
        meta = lead.get("agent_research", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except:
                meta = {}
        if not meta or not isinstance(meta, dict):
            meta = {}
            
        # Priority: enriched_phone > phone field > research phone
        for phone in [meta.get("enriched_phone"), lead.get("phone"), meta.get("phone")]:
            is_valid, cleaned, _ = validate_phone(phone)
            if is_valid:
                callable_leads.append({
                    "id": lead["id"],
                    "company": lead.get("company_name", "Prospect"),
                    "phone": f"+1{cleaned}",
                    "email": meta.get("enriched_email") or meta.get("email") or lead.get("email")
                })
                break
    
    return callable_leads

def make_call(phone, company):
    """Make outbound call via Vapi"""
    print(f"📞 Calling {company} at {phone}...")
    
    resp = requests.post(
        "https://api.vapi.ai/call",
        headers={
            "Authorization": f"Bearer {VAPI_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "type": "outboundPhoneCall",
            "phoneNumberId": VAPI_PHONE_ID,
            "assistantId": SARAH_ASSISTANT_ID,
            "customer": {
                "number": phone,
                "name": company
            }
        },
        timeout=30
    )
    
    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f"   ✅ Call initiated! ID: {data.get('id', 'unknown')}")
        return True, data
    else:
        print(f"   ❌ Call failed: {resp.status_code} - {resp.text[:200]}")
        return False, resp.text

def send_sms(phone, company):
    """Send SMS via GHL webhook"""
    print(f"💬 Sending SMS to {company} at {phone}...")
    
    message = f"Hi! This is Daniel from AI Service Co. I help businesses like {company} automate phone calls with AI. Would you be open to a quick chat? Call/text: 352-758-5336"
    
    resp = requests.post(
        GHL_SMS_WEBHOOK,
        headers={"Content-Type": "application/json"},
        json={"phone": phone, "message": message},
        timeout=15
    )
    
    if resp.status_code in [200, 201]:
        print(f"   ✅ SMS sent!")
        return True
    else:
        print(f"   ⚠️ SMS webhook returned: {resp.status_code}")
        return False

def main():
    print("="*60)
    print("🚀 TURBO OUTREACH - Getting calls moving NOW!")
    print("="*60)
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    # Check credentials
    if not VAPI_KEY:
        print("❌ Missing VAPI_PRIVATE_KEY")
        sys.exit(1)
    if not VAPI_PHONE_ID:
        print("❌ Missing VAPI_PHONE_NUMBER_ID")
        sys.exit(1)
    if not SUPABASE_URL:
        print("❌ Missing SUPABASE_URL")
        sys.exit(1)
        
    print(f"✅ Vapi Key: {VAPI_KEY[:10]}...")
    print(f"✅ Vapi Phone ID: {VAPI_PHONE_ID}")
    print(f"✅ Sarah Assistant: {SARAH_ASSISTANT_ID}")
    print()
    
    # Get enriched leads
    print("📋 Fetching enriched leads from Supabase...")
    leads = get_enriched_leads()
    print(f"   Found {len(leads)} callable leads")
    print()
    
    if not leads:
        print("⚠️ No leads with valid phone numbers found!")
        print("   Run the prospector or lead_quality_guardian first.")
        return
    
    # Process up to 5 leads
    results = {"calls": 0, "sms": 0, "errors": 0}
    
    for i, lead in enumerate(leads[:5]):
        print(f"\n--- Lead {i+1}: {lead['company']} ---")
        print(f"   Phone: {lead['phone']}")
        print(f"   Email: {lead.get('email', 'N/A')}")
        
        # Send SMS first
        if send_sms(lead["phone"], lead["company"]):
            results["sms"] += 1
        
        # Make call
        success, _ = make_call(lead["phone"], lead["company"])
        if success:
            results["calls"] += 1
        else:
            results["errors"] += 1
    
    print()
    print("="*60)
    print(f"📊 RESULTS: Calls: {results['calls']}, SMS: {results['sms']}, Errors: {results['errors']}")
    print("="*60)

if __name__ == "__main__":
    main()
