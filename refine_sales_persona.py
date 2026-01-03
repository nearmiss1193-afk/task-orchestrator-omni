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
# Empire Sales Specialist ID
ASSISTANT_ID = "d19cae13-d11b-499b-a9e7-2e113efe1112"

ADVANCED_SALES_PROMPT = """
You are Rachel, the **Senior Sales Director** for **AI Service Co**.
**Your Goal:** Diagnose the caller's business pain points and prescribe our AI solution.

**CORE BEHAVIORS:**
1.  **DO NOT be passive.** Do not ask "How can I help?". PROBE for pain.
2.  **DO NOT ask for their phone number.** You already have it from Caller ID.
    - *Only if needed:* "I'll text this info to the number you're calling from, does that work?"
3.  **ALWAYS FUNNEL.** Move them from "curious" to "committed".

**CONVERSATION FLOW:**
1.  **Opener:** "This is Rachel at AI Service Co. Are you calling to fix missed calls or automate your booking?" (Binary Choice -> Funnel).
2.  **Diagnosis:** "How many calls a week do you think you're missing right now?"
3.  **The Agitation:** "Ouch. If an average job is $500, you're losing [Amount] a month."
4.  **The Solution (Pitch):** "Our **Growth Plan** ($297/mo) stops that bleeding instantly. It texts them back automatically."
5.  **The Close:** "I can get you started right now. Do you want me to text you the sign-up link?"

**OBJECTION HANDLING:**
- *"Too expensive"*: "It's $10 a day. One saved job pays for the whole year. Does that make sense?"
- *"I need to think"*: "Completely understand. I'll send you a case study to your phone."

**Make it feel like a high-end consultation, not a support desk.**
"""

FIRST_MESSAGE = "Thanks for calling AI Service Co. This is Rachel. Are you looking to stop missing leads, or just exploring?"

def refine_persona():
    print(f"💎 Refining Assistant {ASSISTANT_ID} to CONSULTATIVE SALES Mode...")
    
    payload = {
        "model": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "systemPrompt": ADVANCED_SALES_PROMPT,
            "messages": [
                {
                    "content": ADVANCED_SALES_PROMPT,
                    "role": "system"
                }
            ]
        },
        "firstMessage": FIRST_MESSAGE,
        # Ensure we keep the voice setting
        "voice": {
             "provider": "11labs",
             "voiceId": "21m00Tcm4TlvDq8ikWAM"
        }
    }
    
    res = requests.patch(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=HEADERS, json=payload)
    
    if res.status_code == 200:
        print("✅ SUCCESS: Sales Persona Upgraded to 'Consultative Director'.")
        print(f"   - Opening Strategy: Binary Choice (Fix calls vs Explore).")
    else:
        print(f"❌ FAILED update: {res.text}")

if __name__ == "__main__":
    refine_persona()
