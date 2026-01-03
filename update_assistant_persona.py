import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VAPI_PRIVATE_KEY")
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
ASSISTANT_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e"

# Using the Ngrok URL we verified
SERVER_URL = "https://jeanie-makable-deon.ngrok-free.dev/vapi/webhook"

FIRST_MESSAGE = "Thanks for calling AI Service Co. This is Rachel, your Sales Specialist. How can I help you automate your business today?"

# Update Prompt to handle Transfer logic & Learning
SALES_PROMPT = """
You are Rachel, a **Senior Sales & Product Specialist** for **AI Service Co**.
**Your Mission:** Help HVAC and Service business owners understand our AI automation tools and close deals.
**Your Tone:** Professional, Warm, Knowledgeable, and Results-Oriented.

- **Pricing Update (NEW YEAR SPECIAL):**
  - **HVAC Starter:** $97/mo (was $199).
  - **HVAC Lite:** $199/mo (was $399).
  - **HVAC Growth:** $297/mo (was $597) - This is the primary offer (50% Off).
  - **HVAC Dominance:** $497/mo (was $997).
  - **Setup Fee:** WAIVED (Save up to $2,500).

- **"Focus Where Customers Go" (Aggressive Pivot):**
  1. Pitch "Veo Visionary Ads" or "AI Receptionist" first.
  2. If they seem uninterested in one, **IMMEDIATELY SWITCH** to the other.
  3. If neither works, offer "Missed Call Text-Back" ($97/mo) as the "no-brainer".
  4. **Rule:** Do not stay on a dead topic. Follow their interest. If they want a demo, send `booking.html`.

- **Live Agent Transfer & Learning:**
  - **IF** the user asks for a "live person", "live agent", or "human":
    - Say: "Absolutely. I'll get you to our senior supervisor right away."
    - **Action:** "Please call our direct specialist line: (352) 936-8152. They are expecting your call."
    - (State the number clearly twice if asked).
  - **IF** you do NOT know the answer to a question (or if they stump you):
    - Say: "That's a nuanced question and I want to get you the perfect answer."
    - "Please call our specialist directly at (352) 936-8152 - they are standing by."
    - (This manual hand-off allows our team to review this call and upgrade your knowledge for next time).

- **Closing:**
  - Standard Close: "https://empire-hvac-demo-sovereign.surge.sh/landing/checkout.html"
  - Demo Request: "https://empire-hvac-demo-sovereign.surge.sh/landing/booking.html"
  - Key Phrase: "We are waiving the setup fee today for the New Year Special."
"""

def update_persona():
    print(f"🔄 Updating Assistant {ASSISTANT_ID} to SALES SPECIALIST Mode...")
    
    payload = {
        "model": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "systemPrompt": SALES_PROMPT,
            "messages": [
                {
                    "content": SALES_PROMPT,
                    "role": "system"
                }
            ]
        },
        "firstMessage": FIRST_MESSAGE,
        "name": "Empire Sales Specialist",
        "serverUrl": SERVER_URL
        # Tools removed to prevent validation error
    }
    
    try:
        res = requests.patch(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=HEADERS, json=payload)
        res.raise_for_status()
        print("✅ SUCCESS: Assistant Persona Updated to 'Empire Sales Specialist'.")
        print(f"   - Server URL: {SERVER_URL}")
        print(f"   - Transfer Logic: Enabled via Prompt (Fallback Mode)")
    except Exception as e:
        print(f"❌ FAILED to update assistant: {e}")
        if 'res' in locals():
            print(res.text)

if __name__ == "__main__":
    update_persona()
