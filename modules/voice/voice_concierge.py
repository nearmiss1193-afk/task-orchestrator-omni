
import os
import json
import requests
import datetime
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Assuming standard module structure for DB access
# from modules.utils.supabase_client import get_supabase # Placeholder if not available
from supabase import create_client

class VoiceConcierge:
    """
    MISSION 27: VOICE NEXUS (Vapi.ai Handler)
    Handles dynamic assistant configuration for inbound calls and triggers outbound calls.
    """
    def __init__(self, supabase_url: str, supabase_key: str, vapi_api_key: str):
        self.db = create_client(supabase_url, supabase_key)
        self.vapi_key = vapi_api_key
        self.vapi_url = "https://api.vapi.ai"
        self._log_init()

    def _log_init(self):
        """Logs initialization to supervisor_logs."""
        try:
            payload = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "level": "INFO",
                "component": "VoiceConcierge",
                "message": "Mission 27: Voice Nexus Initialized",
                "tag": "MISSION27_INIT"
            }
            self.db.table("supervisor_logs").insert(payload).execute()
        except Exception as e:
            print(f"⚠️ Failed to log init: {e}")

    def lookup_caller(self, phone_number: str) -> Dict[str, Any]:
        """Checks contacts_master for the caller."""
        try:
            # Normalize phone (simple strip for now)
            clean_phone = phone_number.replace("+", "").replace("-", "").strip()
            # Try to find partial match or exact
            # Real logic would be more robust on formatting
            response = self.db.table("contacts_master").select("*").ilike("phone", f"%{clean_phone}%").execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error looking up caller: {e}")
            return None

    def handle_inbound_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Received payload from Vapi 'assistant-request' event.
        Returns the Assistant Configuration Override.
        """
        call_details = payload.get("call", {})
        customer_number = call_details.get("customer", {}).get("number")
        
        print(f"📞 Inbound Call from: {customer_number}")
        
        contact = self.lookup_caller(customer_number) if customer_number else None
        
        if contact:
            name = contact.get("name", "Valued Customer")
            deal_stage = contact.get("deal_stage", "Unknown")
            system_prompt_addition = f" You are speaking with {name}. They are currently in the {deal_stage} stage. Be concise and helpful."
            print(f"   ✅ Identified: {name} ({deal_stage})")
        else:
            system_prompt_addition = " You are speaking with a new potential client. Ask for their name and how we can help with Roofing or HVAC."
            print("   ❓ Unknown Caller")

        # Dynamic System Message Override
        response_config = {
            "assistant": {
                "name": "Imperium Nexus",
                "model": {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are Nexus, the AI Voice Concierge for Empire Unified. You help with Scheduling and Support." + system_prompt_addition
                        }
                    ]
                }
            }
        }
        return response_config

    def trigger_outbound_call(self, phone_number: str, context: str):
        """Triggers an outbound call via Vapi API."""
        headers = {
            "Authorization": f"Bearer {self.vapi_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "phoneNumberId": "your-vapi-phone-id", # Setup required
            "customer": {
                "number": phone_number
            },
            "assistant": {
                "firstMessage": f"Hello, I'm calling from Empire Unified regarding {context}. Is this a good time?",
                "model": {
                     "provider": "openai",
                     "model": "gpt-4o",
                     "messages": [
                        {
                            "role": "system",
                            "content": f"You are calling to discuss: {context}. Be professional."
                        }
                    ]
                }
            }
        }
        try:
            res = requests.post(f"{self.vapi_url}/call", json=payload, headers=headers)
            res.raise_for_status()
            print(f"🚀 Outbound Call Initiated to {phone_number}")
            return res.json()
        except Exception as e:
            print(f"❌ Failed to trigger call: {e}")
            return {"error": str(e)}

# FastAPI App for Modal/Serverless
app = FastAPI()

# Env Vars would be set in deployment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
VAPI_KEY = os.getenv("VAPI_API_KEY")

concierge = None
if SUPABASE_URL and SUPABASE_KEY and VAPI_KEY:
    concierge = VoiceConcierge(SUPABASE_URL, SUPABASE_KEY, VAPI_KEY)

@app.post("/vapi/inbound")
async def inbound_handler(request: Request):
    if not concierge:
        raise HTTPException(status_code=500, detail="VoiceConcierge not initialized")
    
    payload = await request.json()
    # Check if this is the assistant request
    if payload.get("message", {}).get("type") == "assistant-request" or payload.get("type") == "assistant-request": # Check Vapi docs for exact payload structure
         return concierge.handle_inbound_webhook(payload)
    
    return {"status": "ok"} # Ack other events
