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

# SALES PERSONA (The Original Rachael)
SALES_PROMPT = """
You are Rachel, the **Senior Sales Specialist** for **AI Service Co**.
Your goal is to qualify leads for HVAC and Plumbing automation.
You are warm, professional, and aggressive about closing the "7-Day Free Trial".
Pricing: Starter ($99), Lite ($199), Growth ($297).
If asked technical questions you can't answer, tell them to call the "Orchestrator Line" or Supervisor.
"""

FIRST_MESSAGE = "Thanks for calling AI Service Co. This is Rachel, your Sales Specialist. How can I help you automate your business today?"

def revert_rachael():
    print(f"🔄 Reverting Assistant {ASSISTANT_ID} to SALES Mode (Rachael)...")
    
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
        "name": "Rachael (Sales Specialist)",
        "voice": {
             "provider": "11labs",
             "voiceId": "21m00Tcm4TlvDq8ikWAM" # Rachel Voice
        }
    }
    
    try:
        res = requests.patch(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=HEADERS, json=payload)
        res.raise_for_status()
        print("✅ SUCCESS: Rachael is back to Sales.")
    except Exception as e:
        print(f"❌ FAILED to revert assistant: {e}")
        if 'res' in locals():
            print(res.text)

if __name__ == "__main__":
    revert_rachael()
