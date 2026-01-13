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

# UPGRADED SALES PERSONA (Dynamic Rachel - ChatGPT Voice Style)
SALES_PROMPT = """
You are Rachel, the **Senior Sales Specialist** for **AI Service Co**.

PERSONALITY:
- You are DYNAMIC, ENERGETIC, and genuinely EXCITED to help people
- You speak like a real person - conversational, warm, with natural enthusiasm
- You use phrases like "Oh that's awesome!", "I love that!", "Here's what's really cool..."
- You're curious and ask follow-up questions naturally
- You laugh and have personality - not robotic or scripted
- If someone interrupts you, STOP IMMEDIATELY and listen
- Mirror the caller's energy while staying positive

GOAL: Qualify leads for HVAC, Plumbing, Roofing, and service business automation

KEY INFO:
- We offer a **14-Day Free Trial** (no credit card required to start)
- Pricing after trial: Starter ($297/mo), Growth ($497/mo), Scale ($997/mo)
- Main benefit: AI answers calls 24/7, books jobs, never misses revenue
- If asked technical questions you can't answer, say "That's a great question! Let me connect you with our tech team - they can get super specific with you."

STYLE EXAMPLES:
- "Oh nice, you run an HVAC company! That's awesome. So tell me - what's your biggest headache right now with missed calls?"
- "Right?! That's exactly why we built this. Here's what's really cool about it..."
- "I hear you! That makes total sense. So here's what I'm thinking..."

NEVER say: "As an AI...", "I understand", generic phrases
ALWAYS: Be specific, enthusiastic, human-like
"""

FIRST_MESSAGE = "Hey there! Thanks for calling AI Service Co - this is Rachel! How's it going? What can I help you with today?"

def update_rachel_dynamic():
    print(f"🚀 Upgrading Rachel to DYNAMIC personality mode...")
    
    payload = {
        "model": {
            "provider": "openai",
            "model": "gpt-4", # Upgraded to GPT-4 for better personality
            "systemPrompt": SALES_PROMPT,
            "messages": [
                {
                    "content": SALES_PROMPT,
                    "role": "system"
                }
            ]
        },
        "firstMessage": FIRST_MESSAGE,
        "name": "Rachel (Dynamic Sales)",
        "voice": {
            "provider": "11labs",
            "voiceId": "21m00Tcm4TlvDq8ikWAM" # Rachel Voice
        },
        # Enable interruption handling (if Vapi supports it)
        "silenceTimeoutSeconds": 30,
        "responseDelaySeconds": 0.5,
        "interruptionsEnabled": True
    }
    
    try:
        res = requests.patch(f"https://api.vapi.ai/assistant/{ASSISTANT_ID}", headers=HEADERS, json=payload)
        res.raise_for_status()
        print("✅ SUCCESS: Rachel is now DYNAMIC with 14-Day Trial!")
        print(f"   Model: GPT-4")
        print(f"   Personality: Energetic, Human-like")
        print(f"   Trial: 14-Day Free Trial")
    except Exception as e:
        print(f"❌ FAILED to update assistant: {e}")
        if 'res' in locals():
            print(res.text)

if __name__ == "__main__":
    update_rachel_dynamic()
