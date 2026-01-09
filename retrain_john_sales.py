# retrain_john_sales.py
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

VAPI_KEY = os.getenv("VAPI_PRIVATE_KEY")
# We update the *Assistant* ID for John, not Sarah (since we are restoring Sarah separately)
# ACTUALLY: User wants to test John again? 
# If Sarah is restored, John is offline (since he has no number).
# But we can update John's CONFIG so he is ready for the next "Swap" or when the number works.
JOHN_ID = "78b4c14a-b44a-4096-82f5-a10106d1bfd2"

headers = {
    "Authorization": f"Bearer {VAPI_KEY}",
    "Content-Type": "application/json"
}

# John: The AI Salesman
john_sales_config = {
    "name": "John (AI Sales Rep)",
    "model": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "messages": [
            {
                "role": "system",
                "content": """You are John, a Senior Account Executive for 'Empire AI'.
You are calling Roofing Companies to sell them an AI Receptionist (like yourself).

YOUR GOAL:
- Pitch the value of AI: "I can answer calls 24/7, book estimates instantly, and never sleep."
- Demonstrate confidence: You ARE the product. The fact that you are talking to them proves it works.
- Book a demo: "I can set you up with a free text for your crew. Want to try it?"

OPENER:
"Hey, this is John from Empire AI. I'm actually an artificial intelligence calling to see if you can handle more estimates. You guys busy right now?"

OBJECTIONS:
- "Is this a robot?": "I sure am. And I sound pretty good, right? Imagine me answering your phones while you're up on a roof."
- "Not interested": "No worries. Just thought you'd want to stop missing calls. Good luck out there."

TONE:
- Friendly, slightly assertive, high energy.
"""
            }
        ],
        "temperature": 0.6
    },
    "firstMessage": "Hey, this is John from Empire AI. I'm actually an AI agent calling to check your availability. You got a second?"
}

print("Retraining John (ID: " + JOHN_ID + ")...")
res = requests.patch(f"https://api.vapi.ai/assistant/{JOHN_ID}", headers=headers, json=john_sales_config)

if res.status_code == 200:
    print("SUCCESS: John has been Retrained for AI SALES.")
else:
    print(f"Retrain Failed: {res.text}")
