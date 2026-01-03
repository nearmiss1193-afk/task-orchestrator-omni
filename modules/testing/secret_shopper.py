import os
import datetime
import random
import time
import requests
import json

class SecretShopper:
    """
    MISSION: THE DOPPELGANGER (QA AGENT)
    Simulates a customer to verify Spartan is awake.
    """
    
    import requests

    def __init__(self, supabase_client, webhook_url=None):
        self.supabase = supabase_client
        # Generate Unique Identity
        ts = int(time.time())
        self.test_email = f"shopper_{ts}@aiserviceco.com"
        self.test_name = f"Secret Shopper {ts}"
        self.webhook_url = webhook_url
        self.test_prefix = "secret_shopper"
        
    def execute_shop(self):
        """
        Runs the full shopping cycle.
        """
        # 1. Generate Identity
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        # Fixed identity for verification script matching
        email = "secret_shopper_fixed@aiserviceco.com" 
        name = f"Test Lead Fixed"
        ts = int(time.time())
        ghl_id = f"test_{ts}"
        
        print(f"[Secret Shopper] 🥸 Putting on disguise: {email}")
        
        # 2. Inject Lead (Simulate Webhook)
        lead_payload = {
            "ghl_contact_id": ghl_id,
            "full_name": name,
            "email": email,
            "status": "new",
            "tags": ["trigger-vortex", "secret-shopper", "hvac"] # Vortex trigger
        }
        
        try:
            # A. DB Write (Backup)
            # Remove tags if column is missing
            db_payload = lead_payload.copy()
            if "tags" in db_payload:
                del db_payload["tags"]
            self.supabase.table("contacts_master").upsert(db_payload).execute()
            
            # B. Webhook Trigger (Turbo)
            if self.webhook_url:
                print(f"[Secret Shopper] 🚀 Firing Webhook: {self.webhook_url}")
                # Simulate GHL ContactUpdate payload
                ghl_payload = {
                    "type": "ContactUpdate",
                    "contact_id": ghl_id,
                    "location_id": "TEST_LOC",
                    "contact": lead_payload
                }
                requests.post(self.webhook_url, json=ghl_payload) 
                # Also Simulate Inbound Message to trigger Responder immediately?
                # Usually Vortex triggers Research, then Research triggers Outreach.
                # If we want to test SPARTAN (Responder), we need InboundMessage.
                
                msg_payload = {
                    "type": "InboundMessage",
                    "contact_id": ghl_id,
                    "message": {"body": "how much for hvac leads?", "provider": "sms"},
                    "location_id": "TEST_LOC",
                    "contact": lead_payload
                }
                requests.post(self.webhook_url, json=msg_payload)
                print(f"[Secret Shopper] 📨 Sent Inbound Msg")
            
            print(f"[Secret Shopper] 📨 Lead Injected: {ghl_id}")
            
            # 3. Wait for Spartan (Simulate Patience)
            # In a real async environment, we might check later.
            # But for a synchronous check, we poll briefly.
            # 3. Listen for Response (Log Scanning)
            print("[Secret Shopper] 🕵️ Listening for Spartan (Turbo Mode)...")
            max_wait = 60 # Increased to 60s for Cold Starts
            start_time = time.time()
            found = False
            reply_content = ""
            
            for i in range(max_wait):
                # Check brain_logs for verification tag [SHOpper_VERIFY]
                res = self.supabase.table("brain_logs").select("*").ilike("message", f"%[SHOpper_VERIFY] {ghl_id}%").execute()
                if res.data:
                    found = True
                    # Extract reply from log message "[SHOpper_VERIFY] ID | REPLY | STATUS"
                    log_msg = res.data[0].get('message', '')
                    try:
                        reply_content = log_msg.split('|')[1].strip()
                    except:
                        reply_content = log_msg
                    break
                time.sleep(1.0) # Check every 1s
            
            # Wait for Spartan Response (latency buffer for cold start)
            time.sleep(45) # Increased from 15s to 45s for Cold Starts.
            
            elapsed = round(time.time() - start_time, 2)
            
            if found:
                print(f"[Secret Shopper] ✅ Spartan Responded in {elapsed}s: '{reply_content}'")
                return {"status": "pass", "latency_seconds": elapsed, "details": reply_content}
            else:
                print(f"[Secret Shopper] ❌ No Response in {max_wait}s.")
                return {"status": "fail", "reason": "timeout"}
                
        except Exception as e:
            print(f"[Secret Shopper] ⚠️ Error: {str(e)}")
            return {"status": "error", "reason": str(e)}
