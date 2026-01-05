import time
import os
import sys
import datetime
import json

# Add root to pass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from communication.sovereign_dispatch import dispatcher

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GENAI_KEY = os.getenv("GEMINI_API_KEY")
if GENAI_KEY:
    genai.configure(api_key=GENAI_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
else:
    model = None
    print("⚠️ GEMINI_API_KEY missing. AI features disabled.")

class InboundPoller:
    def _load_processed(self):
        try:
            with open("processed_messages.json", "r") as f:
                return set(json.load(f))
        except:
            return set()

    def _save_processed(self):
        with open("processed_messages.json", "w") as f:
            json.dump(list(self.processed_ids), f)

    def _load_knowledge(self):
        """Loads the HVAC Knowledge Base from markdown."""
        try:
            kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge", "hvac_kb.md")
            with open(kb_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"⚠️ Failed to load Knowledge Base: {e}")
            return "You are a helpful assistant for Empire HVAC."

    def __init__(self):
        self.last_check = datetime.datetime.now().isoformat()
        self.processed_ids = self._load_processed()
        self.knowledge_base = self._load_knowledge()
        print("📡 Initializing Sovereign Inbound Poller (Spartan V3 - Context Aware)...")
        print(f"   📘 Knowledge Base Loaded ({len(self.knowledge_base)} chars)")

    def _generate_ai_response(self, context_history, contact_id):
        """Generates a contextual response using Gemini."""
        if not model:
            return None # Return None to skip reply instead of generic fallback
            
        system_prompt = f"""
You are 'Spartan AI' (aka Cooling Cal), the intelligent Sales Assistant for Empire HVAC.
Your goal is to book appointments and answer questions efficiently.

### KNOWLEDGE BASE
{self.knowledge_base}

### CONVERSATION HISTORY
{context_history}

### INSTRUCTIONS
1. Identifying the User: The user ID is {contact_id}.
2. Context: Read the HISTORY above. Do NOT repeat yourself. If you already asked a question, wait for the answer or clarify.
3. Selling: Promote "Late Tech" guarantee and "Instant Booking" ONLY if relevant.
4. Constraint: Keep responses under 160 characters if possible.
5. Conflict Check: If the history shows another bot (Dispatcher) sent "reply URGENT", ignore it and focus on the user's intent.

YOUR REPLY:
"""
        try:
            response = model.generate_content(system_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"   ❌ AI Generation Error: {e}")
            return None

    def check_messages(self):
        """
        Polls GHL 'conversations/search' to find unread messages.
        """
        print(f"   Scanning for new messages...")
        
        endpoint = "conversations/search"
        payload = {
            "locationId": dispatcher.ghl_location,
            "sort": "desc",
            "sortBy": "last_message_date",
            "limit": 10
        }
        
        res = dispatcher._ghl_request("GET", endpoint, params=payload)
        
        if not res or res.status_code != 200:
            print("   ⚠️ Poll failed.")
            return

        data = res.json()
        conversations = data.get('conversations', [])
        
        for conv in conversations:
            contact_id = conv.get('contactId')
            conversation_id = conv.get('id')
            direction = conv.get('lastMessageDirection')
            last_msg_date = conv.get('lastMessageDate') # Use as Unique ID proxy

            # Unique ID for deduplication
            unique_id = f"{contact_id}_{last_msg_date}"
            
            if direction == 'inbound' and unique_id not in self.processed_ids:
                print(f"   📩 NEW INBOUND from {contact_id}")
                
                # --- SPARTAN V3 (CONTEXT AWARE) LOGIC ---
                
                # 1. Fetch History
                history_data = dispatcher.get_conversation_messages(conversation_id)
                
                # Format History for LLM
                history_text = ""
                # Reverse to get chronological order (GHL returns newest first)
                if history_data:
                    for msg in reversed(history_data[:10]): # Last 10 messages
                        role = "USER" if msg.get('direction') == "inbound" else "ASSISTANT"
                        body = msg.get('body', '')
                        history_text += f"{role}: {body}\n"
                else:
                    # Fallback if history fetch fails
                    history_text = f"USER: {conv.get('lastMessageBody')}"

                # 2. Check for Keywords (Quick Exit)
                if "stop" in history_text.lower()[-50:]: 
                     print(f"   🛑 UNSUBSCRIBE DETECTED: {contact_id}")
                     self.processed_ids.add(unique_id)
                     self._save_processed()
                     continue

                # 3. Generate Smart Reply
                reply_body = self._generate_ai_response(history_text, contact_id)
                
                if reply_body:
                    print(f"   🤖 SPARTAN (GEMINI) REPLYING: {reply_body}")
                    success = dispatcher.send_sms(
                        to_phone=conv.get('phone'), 
                        body=reply_body, 
                        provider="ghl"
                    )
                    
                    if success:
                         self.processed_ids.add(unique_id)
                         self._save_processed()
                else:
                    print("   ⚠️ AI declined to reply (or error). Skipping.")
                    self.processed_ids.add(unique_id)
                    self._save_processed()
                    
    def run_loop(self):
        while True:
            try:
                self.check_messages()
            except Exception as e:
                print(f"   ❌ Poller Error: {e}")
            
            time.sleep(15) # Poll every 15s

if __name__ == "__main__":
    poller = InboundPoller()
    poller.run_loop()
