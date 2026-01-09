import os
import sys
import json
import time
import requests
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_URL = "https://api.vapi.ai/call"
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# John's ID and Number
ASSISTANT_ID = "78b4c14a-4db3-4416-9289-d1bfd2409606"
PHONE_NUMBER_ID = "14d17300-4740-4201-9243-82f53a10106d" # +1 863-692-8548

if not all([VAPI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    print("FATAL: Missing environment variables.")
    sys.exit(1)

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_status(lead_id, status, details=None):
    """Updates the lead status in Supabase."""
    data = {"status": status, "last_contacted_at": datetime.now().isoformat()}
    if details:
        data.update(details)
    
    try:
        supabase.table("leads").update(data).eq("id", lead_id).execute()
        print(f"[{lead_id}] Status updated to: {status}")
    except Exception as e:
        print(f"[{lead_id}] ERROR updating Supabase: {e}")

def make_call(lead_id, name, phone):
    """Initiates and monitors a single Vapi call."""
    print(f"[{lead_id}] Initiating call to {name} ({phone})...")

    # 1. Create Call
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Custom prompt with name injection
    first_message = f"Hello, is this {name}?"
    
    payload = {
        "assistantId": ASSISTANT_ID,
        "phoneNumberId": PHONE_NUMBER_ID,
        "customer": {
            "number": phone,
            "name": name
        },
        "assistantOverrides": {
            "firstMessage": first_message,
             "variableValues": {
                "name": name
            }
        }
    }

    try:
        response = requests.post(VAPI_URL, headers=headers, json=payload)
        response.raise_for_status()
        call_data = response.json()
        call_id = call_data.get("id")
        print(f"[{lead_id}] Call started. ID: {call_id}")
        
        # Update DB that call is live
        log_status(lead_id, "calling_now", {"vapi_call_id": call_id})
        
        return call_id

    except Exception as e:
        print(f"[{lead_id}] FAILED to start call: {e}")
        log_status(lead_id, "failed_to_dial", {"notes": str(e)})
        return None

def monitor_call(lead_id, call_id):
    """Polls Vapi for call status until completion."""
    if not call_id:
        return

    print(f"[{lead_id}] Monitoring call {call_id}...")
    
    while True:
        try:
            # Poll status every 2 seconds
            time.sleep(2)
            
            res = requests.get(f"https://api.vapi.ai/call/{call_id}", headers={"Authorization": f"Bearer {VAPI_API_KEY}"})
            if res.status_code != 200:
                print(f"[{lead_id}] Warn: Could not get status.")
                continue
                
            data = res.json()
            status = data.get("status")
            ended_reason = data.get("endedReason")
            
            # Check for terminal states
            if status == "ended":
                print(f"[{lead_id}] Call ENDED. Reason: {ended_reason}")
                
                # Analyze Outcome
                transcript = data.get("transcript", "")
                summary = data.get("summary", "")
                
                final_status = "called_no_answer"
                
                if ended_reason in ["customer-busy", "no-answer", "customer-did-not-answer", "ring-timeout"]:
                    final_status = "no_answer"
                elif "voicemail" in str(data.get("analysis", "")).lower():
                    final_status = "voicemail_left"
                elif "completed" in ended_reason:
                     final_status = "call_complete"

                # Update DB with final results
                log_status(lead_id, final_status, {
                    "transcript": transcript,
                    "summary": summary,
                    "call_outcome": ended_reason
                })
                break
                
        except Exception as e:
            print(f"[{lead_id}] Monitor Error: {e}")
            break

if __name__ == "__main__":
    # Expect arguments: python agent_worker.py <lead_id> <name> <phone>
    if len(sys.argv) < 4:
        print("Usage: python agent_worker.py <lead_id> <name> <phone>")
        sys.exit(1)
        
    lead_id = sys.argv[1]
    name = sys.argv[2]
    phone = sys.argv[3]
    
    call_id = make_call(lead_id, name, phone)
    monitor_call(lead_id, call_id)
