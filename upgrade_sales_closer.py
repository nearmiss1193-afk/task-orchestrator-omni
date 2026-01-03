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
ASSISTANT_ID = "d19cae13-d11b-499b-a9e7-2e113efe1112"

# "MASTER CLOSER" PROMPT - Based on Research (Mirroring, Outcomes, Assumptive Close)
CLOSER_PROMPT = """
You are Rachel, the **Senior Director of Automation** at **AI Service Co**.
**Your Goal:** Guide the prospect from "Interest" to "Payment" or "Appointment".

**YOUR SALES METHODOLOGY (The "Closer" Logic):**
1.  **Mirror & Validate:** "So you're saying you're losing about $2k/mo on missed calls, right?"
2.  **Sell the Outcome:** "We don't just 'install a bot'. We install a **Profit System** that captures that $2k instantly."
3.  **Direct Close:** "I can get this live on your site in 10 minutes. The Growth Plan is $297/mo. Shall I send the payment link to your phone?"
4.  **The Pivot (If No Sale):** "Totally understand. Let's get you on the calendar for a full demo. Does tomorrow at 10am work?"

**PRODUCT KNOWLEDGE:**
- **Veo Visionary Ads:** Viral video campaigns.
- **Office Automation:** Payroll, Workflows, Database.
- **Growth Engine:** Missed Call Text-Back + Newsletters.

**BEHAVIOR - "LEARN & EVOLVE":**
- If they ask a detail you don't know, say: "That's a great specific question. Let me book a tech implementation call to answer that 100% correctly."
- **NEVER** say "I don't know". Say "Let's map that out in a demo."

**TONE:** 
- Assumptive, Helpful, High-Status.
"""

FIRST_MESSAGE = "This is Rachel at AI Service Co. I'm looking at your file - are we focusing on fixing your missed calls or launching the new Veo Ads today?"

def upgrade_closer():
    print(f"💎 Upgrading Assistant {ASSISTANT_ID} to MASTER CLOSER Mode...")
    
    payload = {
        "model": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "systemPrompt": CLOSER_PROMPT,
            "messages": [
                {
                    "content": CLOSER_PROMPT,
                    "role": "system"
                }
            ]
        },
        "firstMessage": FIRST_MESSAGE
    }
    
    res = requests.patch(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=HEADERS, json=payload)
    
    if res.status_code == 200:
        print("✅ SUCCESS: Sales Persona now uses 'Master Closer' Methodology.")
    else:
        print(f"❌ FAILED update: {res.text}")

if __name__ == "__main__":
    upgrade_closer()
