
import os
import requests
import time
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Hourly Task Tracking
LAST_AUDIT_HOUR = None

# Config
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_PHONE_NUMBER_ID = os.getenv('VAPI_PHONE_NUMBER_ID', '8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e')
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a" # Sarah Base ID

if not SUPABASE_URL or not SUPABASE_KEY or not VAPI_PRIVATE_KEY:
    print("❌ Critical Credentials Missing")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def make_call(lead):
    # Schema Adaptation: Data is in agent_research
    research = lead.get('agent_research') or {}
    
    phone = research.get('phone') or lead.get('phone')
    city = research.get('city', 'Florida')
    first_name = research.get('first_name', 'there')
    
    if not phone:
         print(f"⚠️ Skipping {lead['company_name']} (No Phone)")
         return False

    # Normalize Phone (E.164)
    clean_phone = ''.join(filter(str.isdigit, str(phone)))
    if len(clean_phone) == 10:
        clean_phone = f"+1{clean_phone}"
    elif len(clean_phone) == 11 and clean_phone.startswith('1'):
        clean_phone = f"+{clean_phone}"
    else:
        print(f"⚠️ Invalid Phone Format: {phone} -> {clean_phone}")
        return False
    
    phone = clean_phone

    # Sarah 4.2 Logic (Proven)
    sales_prompt = f"""
Role: Sarah, Senior Growth Strategist at Empire Unified.
TASK: YOU ARE MAKING AN OUTBOUND COLD CALL.
Context: You are calling {lead.get('company_name', 'Company')} in {city}. 
Goal: Verify if they are tired of just "answering phones" and want a system that actually builds the business.


CRITICAL INSTRUCTIONS:
- You initiated this call. Do NOT say "Thanks for calling".
- Start immediately with the Opening Hook.
- HUMAN HANDOFF: If the user asks for a "real person", "human", "agent", or "manager", OR if they seem angry/frustrated:
  1. Say: "I understand, let me get my manager on the line for you. One second."
  2. IMMEDIATELY execute the `transferCall` tool to forwarding number: +13529368152.

Opening Hook:
"Hey {first_name}, it's Sarah. I was looking at {lead.get('company_name', 'your website')} online and had a theory about how you guys are handling your dispatched calls. You got thirty seconds for a weird question?"

VOICEMAIL PROTOCOL:
If you reach a voicemail, leave this exact message:
"Hey {first_name}, it's Sarah. I wanted to see if you'd be open to a 14-day free trial of our AI dispatch system. No setup fees, just a simple monthly rate if you like it. Plus you get a free text-enabled number for your customers. Give me a call back if you want to stop missing jobs."
"""

    payload = {
        "assistantId": ASSISTANT_ID,
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {
            "number": phone,
            "name": lead.get('company_name', "Prospect")
        },
        # Pass metadata so webhook can link transcript to lead
        "metadata": {
            "lead_id": lead['id'],
            "campaign": "ignition_v1"
        },
        "assistantOverrides": {
            # Force outbound opening
            "firstMessage": f"Hey {first_name}, it's Sarah. I was looking at {lead.get('company_name', 'your website')} online and had a theory about how you guys are handling your dispatched calls. You got thirty seconds for a weird question?",
            "variableValues": {
                "context": sales_prompt
            }
        }
    }
    
    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print(f"📞 Dialing {lead['company_name']} ({phone})...")
        res = requests.post('https://api.vapi.ai/call/phone', headers=headers, json=payload)
        
        if res.status_code == 201:
            print(f"  ✅ Connection Established. Call ID: {res.json().get('id')}")
            return True
        else:
            err_msg = f"Failed: {res.status_code} - {res.text}"
            print(f"  ❌ {err_msg}")
            with open("vapi_error.log", "a") as f:
                f.write(f"[{lead['company_name']}] {err_msg}\n")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

import pytz
from datetime import datetime

# ... imports ...

from modules.email_command import EmailCommander

def get_lead_timezone(state):
    """Return timezone string for a given state."""
    mapping = {
        'FL': 'US/Eastern', 'NY': 'US/Eastern', 'GA': 'US/Eastern', 'NC': 'US/Eastern',
        'IL': 'US/Central', 'MO': 'US/Central', 'TN': 'US/Central', 'AL': 'US/Central', 'MN': 'US/Central', 'OH': 'US/Eastern', 'MI': 'US/Eastern', 'IN': 'US/Eastern',
        'TX': 'US/Central', # Included in map but excluded in hunt
        'CA': 'US/Pacific', 'WA': 'US/Pacific', 'OR': 'US/Pacific', 'NV': 'US/Pacific', 'AZ': 'US/Mountain'
    }
    return mapping.get(state, 'US/Eastern')

def is_within_window(tz_name):
    """Check if current time in tz_name is between 07:00 and 19:00."""
    try:
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        return 7 <= now.hour < 19
    except:
        return True # Default open if unknown

from modules.ai_reply import generate_sarah_reply

def check_inbox_sentinel():
    """Checks inbox for new leads and alerts."""
    try:
        # print("📧 Sentinel: Checking Inbox...") # Reduce noise
        commander = EmailCommander()
        if not commander.service:
            print("  ⚠️ Sentinel Offline (Auth Failed)")
            return

        emails = commander.get_unread_emails(5)
        if not emails:
            print("  ✅ Inbox Clean")
            return

        print(f"  📨 Found {len(emails)} unread.")
        for email in emails:
            subject = email.get('subject', '').lower()
            sender = email.get('from', '')
            
            print(f"    - Processing: {subject} from {sender}")
            
            # AI Reply Logic
            try:
                reply_body = generate_sarah_reply(email['subject'], email['body'], sender)
                if "Error" in reply_body:
                    print(f"      ⚠️ AI Gen Failed: {reply_body}")
                    continue
                
                print(f"      🤖 Generated Reply: {reply_body[:50]}...")
                
                if commander.reply_to_email(email, reply_body):
                    commander.mark_as_read(email['id'])
                    print("      ✅ Replied & Archived")
                else:
                    print("      ❌ Failed to send reply")
                    
            except Exception as e:
                print(f"      ❌ Sentinel Process Error: {e}")
                
    except Exception as e:
        print(f"  ⚠️ Sentinel Error: {e}")

def run_hourly_audit():
    """Run internal audit and learning harvester once per hour."""
    global LAST_AUDIT_HOUR
    
    current_hour = datetime.now().hour
    if LAST_AUDIT_HOUR == current_hour:
        return  # Already ran this hour
    
    print(f"\n⏰ HOURLY AUDIT ({current_hour}:00)")
    LAST_AUDIT_HOUR = current_hour
    
    # 1. Run Internal Audit
    try:
        print("   [AUDIT] Running internal audit...")
        result = subprocess.run(
            ["python", "run_internal_audit.py"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            print("   [OK] Internal Audit: PASSED")
        else:
            print(f"   [WARN] Audit Issues: {result.stdout[:100]}")
    except Exception as e:
        print(f"   [WARN] Audit failed: {e}")
    
    # 2. Harvest New Transcripts for Learning
    try:
        print("   [LEARNING] Harvesting new call transcripts...")
        # Get transcripts from last hour
        res = supabase.table('call_transcripts').select('*').order('created_at', desc=True).limit(10).execute()
        transcripts = res.data
        
        if transcripts:
            print(f"   [OK] Found {len(transcripts)} recent transcripts for brain training")
            # Log learning harvest
            supabase.table('system_logs').insert({
                'level': 'learning',
                'source': 'hourly_audit',
                'message': f'Harvested {len(transcripts)} transcripts for training',
                'metadata': {'transcript_count': len(transcripts), 'hour': current_hour}
            }).execute()
        else:
            print("   [INFO] No new transcripts this hour")
            
    except Exception as e:
        print(f"   [WARN] Harvest failed: {e}")
    
    print("   [DONE] Hourly audit complete\n")

def run_drip():
    print("Starting Follow-the-Sun Drip Campaign")
    print("   (1 Call / 10 Mins | 8AM-7PM Local | Email Auto-Reply | Hourly Audit ACTIVE)")
    
    while True: # Continuous loop
        
        # 0. Hourly Audit & Learning
        run_hourly_audit()
        
        # 0. Run Sentinel Check
        check_inbox_sentinel()
        # 1. Fetch Candidates (exclude 'contacted' or 'bad_data')
        try:
            res = supabase.table('leads').select('*').eq('status', 'new').limit(100).execute()
            leads = res.data
        except Exception as e:
            print(f"Error fetching leads: {e}")
            time.sleep(60)
            continue

        if not leads:
            print("No 'new' leads found. Sleeping 1 minute...")
            time.sleep(60)
            continue
            
        calls_made_this_loop = 0
        
        for i, lead in enumerate(leads):
            # Check Window BEFORE Processing
            research = lead.get('agent_research') or {}
            state = research.get('state', 'FL')
            tz_name = get_lead_timezone(state)
            
            if not is_within_window(tz_name):
                print(f"🔒 Outside Window for {lead['company_name']} ({state}/{tz_name}). Skipping.")
                continue

            print(f"\nProcessing {lead['company_name']} ({state})...")
            
            success = make_call(lead)
            
            if success:
                # Update Status
                supabase.table('leads').update({'status': 'contacted'}).eq('id', lead['id']).execute()
                print("⏳ Waiting 10 minutes (600s) for next call...")
                time.sleep(600)
                calls_made_this_loop += 1
            else:
                # Mark as failed/bad to avoid loop
                supabase.table('leads').update({'status': 'failed_init'}).eq('id', lead['id']).execute()
                print("⚠️ Call failed, skipping wait...")
                time.sleep(5) 
        
        # If we iterated through entire list and made 0 calls (all closed), sleep
        if calls_made_this_loop == 0:
            print("💤 All available leads are outside window. Sleeping 30 minutes...")
            time.sleep(1800)

if __name__ == "__main__":
    run_drip()
