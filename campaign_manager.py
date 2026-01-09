import time
import os
import sys
import subprocess
import threading
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Configuration ---
MAX_CONCURRENT_WORKERS = 3  # Vapi Limit
WARMUP_MINUTES = 5

def get_email_targets():
    """Fetch leads ready for Step 1: Email"""
    try:
        res = supabase.table("leads").select("*").eq("status", "ready_to_send").limit(1).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"DB Error (Email Fetch): {e}")
        return None

def get_call_targets():
    """Fetch leads ready for Step 2: Call (after warmup)"""
    try:
        # We need to filter manually for time diff since Supabase simple queries might be limited
        res = supabase.table("leads").select("*").eq("status", "warming_up").limit(10).execute()
        
        now = datetime.now()
        ready_leads = []
        
        for lead in res.data:
            sent_at_str = lead.get('email_sent_at')
            if not sent_at_str:
                continue
                
            sent_at = datetime.fromisoformat(sent_at_str)
            if now - sent_at > timedelta(minutes=WARMUP_MINUTES):
                return lead
                
        return None
    except Exception as e:
        print(f"DB Error (Call Fetch): {e}")
        return None

def mark_processing(lead_id, stage):
    status = "processing_email" if stage == "email" else "processing_call"
    supabase.table("leads").update({"status": status}).eq("id", lead_id).execute()

def email_worker(lead):
    """Executes Step 1"""
    company = lead.get('company_name') or "Unknown Company"
    email = lead.get('email')
    
    if not email:
        print(f"[MANAGER] SKIP: No email for {company}")
        supabase.table("leads").update({"status": "ready_to_call", "notes": "Skipped email (missing)"}).eq("id", lead['id']).execute()
        return

    print(f"[MANAGER] Sending Email to {company}...")
    mark_processing(lead['id'], "email")
    
    # Run script with explicit python executable and environment
    cmd = [sys.executable, "send_email.py", str(lead['id']), str(company), str(email)]
    # Capture output to catch crashes
    res = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())
    
    if res.returncode != 0:
        print(f"[MANAGER] 🚨 CRASH in send_email.py for {company}!")
        error_msg = res.stderr[-200:] if res.stderr else "Unknown Error"
        print(f"Error: {error_msg}")
        # Auto-Recover: Mark as error so it doesn't block queue
        supabase.table("leads").update({
            "status": "system_crash", 
            "notes": f"Email Script Crash: {error_msg}"
        }).eq("id", lead['id']).execute()

def call_worker(lead):
    """Executes Step 2"""
    company = lead.get('company_name') or "Unknown"
    print(f"[MANAGER] Warmed up! Calling {company}...")
    mark_processing(lead['id'], "call")
    
    phone_data = lead.get('agent_research', {})
    if not phone_data:
        # Fallback or skip
        print(f"[MANAGER] SKIP: No phone data for {company}")
        supabase.table("leads").update({"status": "failed_data"}).eq("id", lead['id']).execute()
        return

    phone = phone_data.get('phone')
    name = phone_data.get('name', 'Boss')
    
    if not phone:
         print(f"[MANAGER] SKIP: No phone number for {company}")
         supabase.table("leads").update({"status": "failed_data"}).eq("id", lead['id']).execute()
         return

    # Run script - swarm worker style
    cmd = [sys.executable, "agent_worker.py", str(lead['id']), str(name), str(phone)]
    # Capture output
    res = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())

    if res.returncode != 0:
        print(f"[MANAGER] 🚨 CRASH in agent_worker.py for {company}!")
        error_msg = res.stderr[-200:] if res.stderr else "Unknown Error"
        print(f"Error: {error_msg}")
        # Auto-Recover
        supabase.table("leads").update({
            "status": "system_crash", 
            "notes": f"Call Script Crash: {error_msg}"
        }).eq("id", lead['id']).execute()

def main():
    print("=========================================")
    print(f"   FOOFER CAMPAIGN MANAGER (Pacing: {WARMUP_MINUTES}m)")
    print("=========================================")
    
    active_call_threads = []
    
    while True:
        # 1. Clean threads
        active_call_threads = [t for t in active_call_threads if t.is_alive()]
        
        # 2. Check for Email Targets (Unlimited concurrency essentially, but let's throttle to 1 at a time for safety)
        email_lead = get_email_targets()
        if email_lead:
            email_worker(email_lead) # Run blocking for safety/rate limits
            continue # Loop again
            
        # 3. Check for Call Targets (Respect Concurrency)
        if len(active_call_threads) < MAX_CONCURRENT_WORKERS:
            call_lead = get_call_targets()
            if call_lead:
                t = threading.Thread(target=call_worker, args=(call_lead,))
                t.start()
                active_call_threads.append(t)
            else:
                pass # No calls ready
        
        print(f"[STATUS] Calls: {len(active_call_threads)}/{MAX_CONCURRENT_WORKERS} | Waiting...", end="\r")
        time.sleep(5)

if __name__ == "__main__":
    main()
