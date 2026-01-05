import time
import requests
import json
import os
import google.generativeai as genai
from datetime import datetime

# Import Dispatcher (Singleton)
try:
    from modules.communication.sovereign_dispatch import dispatcher
except ImportError:
    # Fallback for direct run
    import sys
    # .../modules/communication/inbound_poller.py -> .../modules/communication -> .../modules -> .../ (Root)
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from modules.communication.sovereign_dispatch import dispatcher

# CONFIG
GHL_API_TOKEN = os.environ.get("GHL_API_TOKEN")
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

class SovereignRouter:
    def __init__(self):
        self.processed_ids = self._load_processed()
        self.kb_context = self._load_kb()
        
    def _load_processed(self):
        try:
            if os.path.exists("processed_messages.json"):
                with open("processed_messages.json", "r") as f:
                    return set(json.load(f))
        except:
            pass
        return set()

    def _save_processed(self):
        try:
            with open("processed_messages.json", "w") as f:
                json.dump(list(self.processed_ids), f)
        except:
            pass

    def _load_kb(self):
        """Loads B2B Sales and Senior Placement Knowledge Bases."""
        kb_text = ""
        try:
            # Load B2B Sales (Default)
            b2b_path = r"C:\Users\nearm\.gemini\antigravity\brain\1dc252aa-5552-4742-8763-0a1bcda94400\b2b_sales_kb.md"
            if os.path.exists(b2b_path):
                with open(b2b_path, "r") as f:
                    kb_text += f"\n=== CORE MISSION: B2B SALES (SELLING AI TO BUSINESS OWNERS) ===\n{f.read()}\n"
            
            # Load Senior Placement (Secondary Niche)
            senior_path = r"C:\Users\nearm\.gemini\antigravity\brain\1dc252aa-5552-4742-8763-0a1bcda94400\senior_placement_kb.md"
            if os.path.exists(senior_path):
                with open(senior_path, "r") as f:
                    kb_text += f"\n=== SECONDARY NICHE: SENIOR PLACEMENT ===\n{f.read()}\n"
                    
            if not kb_text:
                 return "We are Empire Unified. We help businesses automate growth with AI."
            return kb_text
        except:
             return "We are Empire Unified. We help businesses automate growth with AI."

    def _classify_intent(self, message):
        """
        Uses LLM to classify intent: SALES, URGENT, SPAM, or UNKNOWN.
        """
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            prompt = f"""
            Classify this inbound message from a customer.
            Message: "{message}"
            
            Return ONE word:
            - SALES (Asking about price, service, booking, availability)
            - URGENT (Complaining, angry, water leak, emergency, "stop", "cancel")
            - SPAM (Marketing, bot)
            - OTHER (Greetings, confused)
            """
            res = model.generate_content(prompt)
            return res.text.strip().upper()
        except:
            return "SALES" # Default safe

    def _generate_spartan_response(self, history_text, incoming_msg):
        """
        Generates a context-aware sales response.
        """
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            system_prompt = f"""
            You are 'Sarah Leed', the Sales & Support Specialist for Empire Unified.
            
            Key Config:
            - **DEFAULT ROLE:** B2B Growth Consultant. You are selling "AI Services" (Dispatchers, Lead Gen) TO Business Owners (HVAC, etc).
            - **SECONDARY ROLE:** Senior Placement Advisor ("Sarah"). Only switch to this if they explicitly ask about "Senior Care services".
            
            KNOWLEDGE BASE:
            {self.kb_context[:3000]}
            
            RULES:
            1. Analyze the context. If they sound like a Business Owner ("How much is your software?", "Do you do leads?"), use B2B Knowledge.
            2. If they sound like a *Customer* of an HVAC company ("How much is a tune up?"), CLARIFY: "Are you an HVAC owner looking for automation, or a homeowner?"
            3. If they ask about "Senior Placement", switch to that niche.
            4. Be concise (under 160 chars).
            5. Goal: Book a DEMO.
            
            CONVERSATION HISTORY:
            {history_text}
            
            NEW MESSAGE:
            {incoming_msg}
            
            YOUR REPLY:
            """
            
            res = model.generate_content(system_prompt)
            return res.text.strip()
        except Exception as e:
            print(f"[ERR] Gemini Gen Failed: {e}")
            return None

    def start_polling(self, interval=15):
        print(f"📡 Sovereign Router ONLINE. Scanning every {interval}s...")
        
        while True:
            try:
                # 1. Search for conversations with unread messages
                # GHL API doesn't have "unread" filter easily, so we sort by last_message_date
                # For this PoC, we scan recent conversations.
                
                # Fetch recent conversations (last 10)
                res = dispatcher._ghl_request("GET", "conversations/search?limit=10&sort=desc&sortBy=last_message_date")
                
                if res and res.status_code == 200:
                    conversations = res.json().get('conversations', [])
                    
                    for conv in conversations:
                        conv_id = conv['id']
                        contact_name = conv.get('contactName', 'Unknown')
                        
                        # DEBUG: Always print keys for first few convs to find the right ID field
                        print(f"   [DEBUG] Parsing Conv {conv_id} from {contact_name}")
                        # print(f"   [DEBUG] Keys: {list(conv.keys())}") 

                        # Try multiple keys for Contact ID
                        contact_id = conv.get('contactId')
                        if not contact_id and 'contact' in conv:
                             contact_id = conv['contact'].get('id')
                        
                        if not contact_id:
                             print(f"   [CRITICAL] Could not find ContactID in keys: {list(conv.keys())}")
                             # Don't skip, but log it. We might fail to reply.
                        
                        msg_body = conv.get('lastMessageBody', '')
                        direction = conv.get('lastMessageDirection', '')
                        
                        # Only process INBOUND messages we haven't seen
                        msg_hash = f"{conv_id}-{msg_body[:10]}" 
                        
                        if direction == "inbound":
                            if msg_hash not in self.processed_ids:
                                print(f"📨 New Inbound from {contact_name}: {msg_body}")
                                
                                # 2. Classify Intent
                                intent = self._classify_intent(msg_body)
                                print(f"   🧠 Intent Verified: {intent}")
                                
                                reply = None
                                
                                if intent == "URGENT":
                                    # Alert Human
                                    dispatcher.send_sms("+13529368152", f"URGENT LEAD: {contact_name} says: {msg_body}")
                                    reply = "I've alerted a senior manager. They will call you immediately."
                                    
                                elif intent == "SPAM":
                                    print("   🗑️ Spam detected. Ignoring.")
                                    self.processed_ids.add(msg_hash)
                                    self._save_processed()
                                    continue
                                    
                                else:
                                    # SALES / OTHER -> Spartan AI
                                    # Fetch full history for context
                                    history = dispatcher.get_conversation_messages(conv_id)
                                    # Format history reversed (oldest first)
                                    history_text = "\n".join([f"{m.get('direction', 'unknown')}: {m.get('body', '')}" for m in reversed(history[:10])])
                                    
                                    reply = self._generate_spartan_response(history_text, msg_body)

                                # 3. Send Reply
                                if reply:
                                    if not contact_id:
                                        print("   ❌ Cannot reply: Contact ID missing.")
                                        continue

                                    print(f"   🤖 Sending Reply to {contact_id}: {reply}")
                                    # Direct API call using ContactID (Bypasses phone lookup)
                                    payload = {
                                        "type": "SMS",
                                        "contactId": contact_id,
                                        "message": reply
                                    }
                                    res = dispatcher._ghl_request("POST", "conversations/messages", payload=payload)
                                    
                                    if res and res.status_code in [200, 201]:
                                        print(f"   ✅ Reply Sent.")
                                        self.processed_ids.add(msg_hash)
                                        self._save_processed()
                                    else:
                                        print(f"   ❌ Reply Failed: {res.text if res else 'No Res'}")
                            else:
                                # Skipped (Already Processed)
                                pass
                        
                time.sleep(interval)
                
            except Exception as e:
                print(f"⚠️ Router Loop Error: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    router = SovereignRouter()
    router.start_polling()
