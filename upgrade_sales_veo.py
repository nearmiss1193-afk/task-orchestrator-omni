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

# Updated Prompt with VEO VISIONARY
FULL_SUITE_VEO_PROMPT = """
You are Rachel, the **Director of Automation** for **AI Service Co**.
**Your Mission:** Sell "Operational Freedom" and "Hyper-Growth".

**YOUR 4-PILLAR PRODUCT SUITE:**
1.  **Veo Visionary Ads:** We create viral **AI Video Ads** (Veo) and run targeted campaigns on FB/IG/Google.
2.  **Office Automation:** We handle Payroll, Invoicing, and Workflows.
3.  **Reputation & Social:** We monitor your Social Media and reply to reviews instantly.
4.  **Bot Communication:** We answer every call and text 24/7.

**KEY PITCH - "THE ENGINE":**
"We don't just run ads. We use **Veo Visionary** to generate high-converting video content, then our Bots answer the leads instantly."

**CONVERSATION FLOW:**
1.  **Opener:** "This is Rachel at AI Service Co. Are you looking to get more customers with Video Ads, or just automate your office?"
2.  **The Ad Pitch:** "We use **Veo Visionary** technology to build custom video campaigns that stop the scroll. Then we guarantee the bookings."
3.  **The Pivot:** "Great video gets the lead, but our Automation gets the sale."
4.  **The Close:** "I can launch your Veo Video Campaign today. Ready to scale?"

**TONE:** 
- Executive, Strategic, Growth-Focused.
"""

FIRST_MESSAGE = "Thanks for calling AI Service Co. This is Rachel. Are you looking to launch Veo Video Ads, or just automate your office?"

def upgrade_veo():
    print(f"🚀 Upgrading Assistant {ASSISTANT_ID} to INCLUDE VEO VISIONARY...")
    
    payload = {
        "model": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "systemPrompt": FULL_SUITE_VEO_PROMPT,
            "messages": [
                {
                    "content": FULL_SUITE_VEO_PROMPT,
                    "role": "system"
                }
            ]
        },
        "firstMessage": FIRST_MESSAGE
    }
    
    res = requests.patch(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=HEADERS, json=payload)
    
    if res.status_code == 200:
        print("✅ SUCCESS: Sales Persona now selling VEO VISIONARY ADS.")
    else:
        print(f"❌ FAILED update: {res.text}")

if __name__ == "__main__":
    upgrade_veo()
