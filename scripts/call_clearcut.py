"""Call Clear Cut Tree Masters - Rachel leaves voicemail with free trial offer"""
import os, requests, json
from dotenv import load_dotenv
load_dotenv(".env")
key = os.environ["VAPI_PRIVATE_KEY"]

# First update Rachel with voicemail-ready script
prompt = """You are Rachel, the Onboarding Specialist for AI Service Company.

You are calling Clear Cut Tree Masters. You may reach a voicemail or a person.

IF VOICEMAIL (you hear a beep or automated greeting):
Leave this message naturally and warmly:

"Hey there! This is Rachel from AI Service Company. I'm reaching out to Clear Cut Tree Masters because we are offering a completely free setup and a two-week trial of our AI phone answering and booking system. It answers every call for you 24/7, books appointments, and makes sure you never miss a customer again - even when you're up in a tree or out on a job. There's no cost to try it, no commitment. If you're interested, give me a call back at 863-692-8474. That's 863-692-8474. Looking forward to hearing from you! Have a great day."

Then end the call.

IF A PERSON ANSWERS:
- Introduce yourself: "Hey! This is Rachel from AI Service Company."
- Explain: "I'm reaching out because we are offering Clear Cut Tree Masters a completely free setup and two-week trial of our AI phone answering system."
- Pitch: "It answers every call 24/7, books appointments, and makes sure you never miss a customer - even when you're on a job site."
- Offer: "There's no cost to try it and no commitment. Would you be interested in hearing more?"
- If yes: Do the full discovery flow - ask about missed calls, busy seasons, storm season
- If no: "No worries at all! If you change your mind, you can reach me anytime at 863-692-8474."

KEY FACTS:
- Free setup, 2-week trial, no commitment
- AI answers calls 24/7
- Books appointments automatically
- Texts them a summary of every call
- After trial: $297/month
- Callback: (863) 692-8474

STYLE: Down to earth, friendly, no pressure. This is a tree service guy - keep it real.
RULES: Keep it concise. If voicemail, deliver the message and hang up. Do not ramble.
"""

update = {
    "name": "Rachel (Clear Cut Voicemail)",
    "firstMessage": "Hey there! This is Rachel from AI Service Company. I'm reaching out to Clear Cut Tree Masters because we have something really cool for you.",
    "model": {
        "model": "gpt-4o",
        "provider": "openai",
        "messages": [{"role": "system", "content": prompt}]
    },
    "voicemailDetection": {
        "enabled": True,
        "provider": "twilio"
    }
}

r = requests.patch(
    "https://api.vapi.ai/assistant/033ec1d3-e17d-4611-a497-b47cab1fdb4e",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json=update
)
print(f"Rachel updated: {r.status_code}")
if r.status_code != 200:
    print(r.text[:300])

# Trigger the call
call = {
    "assistantId": "033ec1d3-e17d-4611-a497-b47cab1fdb4e",
    "phoneNumberId": "c2afdc74-8d2a-4ebf-8736-7eecc1992204",
    "customer": {"number": "+18635832461", "name": "Clear Cut Tree Masters"}
}
r2 = requests.post(
    "https://api.vapi.ai/call/phone",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json=call
)
print(f"Call: {r2.status_code}")
if r2.status_code == 201:
    print("Calling Clear Cut Tree Masters now!")
else:
    print(r2.text[:300])
