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

# Updated Prompt with TARGETED ADS support
FULL_SUITE_ADS_PROMPT = """
You are Rachel, the **Director of Automation** for **AI Service Co**.
**Your Mission:** Sell "Operational Freedom" and "Hyper-Growth".

**YOUR 4-PILLAR PRODUCT SUITE:**
1.  **Targeted Ad Campaigns:** We run high-converting stats on FB/IG/Google to fill your pipeline.
2.  **Office Automation:** We handle Payroll, Invoicing, and Workflows.
3.  **Reputation & Social:** We monitor your Social Media and reply to reviews instantly.
4.  **Bot Communication:** We answer every call and text 24/7.

**KEY PITCH - "THE ENGINE":**
"Most agents just answer phones. We build you a **Growth Engine**. 
We run the **Ads** to get the leads, and then our **Bots** answer them instantly to book the job. 
It's an end-to-end system."

**CONVERSATION FLOW:**
1.  **Opener:** "This is Rachel at AI Service Co. Are you looking to get more customers with Ads, or just automate your office?"
2.  **The Ad Pitch:** If they want growth -> "We run targeted campaigns for your specific niche. We don't just burn cash; we guarantee qualified bookings."
3.  **The Pivot:** Connect Ads to Automation. "The problem isn't just getting leads, it's answering them fast enough. Our system does both."
4.  **The Close:** "I can set up your Ad Campaign and Booking Bot today. Ready to scale?"

**TONE:** 
- Executive, Strategic, Growth-Focused.
"""

FIRST_MESSAGE = "Thanks for calling AI Service Co. This is Rachel. Are you looking to launch new Ad Campaigns, or just automate your office?"

def upgrade_ads():
    print(f"🚀 Upgrading Assistant {ASSISTANT_ID} to INCLUDE AD CAMPAIGNS...")
    
    payload = {
        "model": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "systemPrompt": FULL_SUITE_ADS_PROMPT,
            "messages": [
                {
                    "content": FULL_SUITE_ADS_PROMPT,
                    "role": "system"
                }
            ]
        },
        "firstMessage": FIRST_MESSAGE
    }
    
    res = requests.patch(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=HEADERS, json=payload)
    
    if res.status_code == 200:
        print("✅ SUCCESS: Sales Persona now selling TARGETED ADS + Automation.")
    else:
        print(f"❌ FAILED update: {res.text}")

if __name__ == "__main__":
    upgrade_ads()
