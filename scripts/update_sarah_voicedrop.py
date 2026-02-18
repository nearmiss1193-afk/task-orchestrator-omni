"""Update Sarah with voice drop campaign knowledge + SMS auto-reply logic"""
import os, requests, json
from dotenv import load_dotenv
load_dotenv(".env")
key = os.environ["VAPI_PRIVATE_KEY"]

# Get Sarah's current prompt
r = requests.get(
    "https://api.vapi.ai/assistant/ae717f29-6542-422f-906f-ee7ba6fa0bfe",
    headers={"Authorization": f"Bearer {key}"}
)
d = r.json()
current_prompt = d.get("model", {}).get("messages", [{}])[0].get("content", "")
print(f"Current prompt length: {len(current_prompt)}")
print(f"First 200 chars: {current_prompt[:200]}")

# Check phone assignment
r2 = requests.get(
    "https://api.vapi.ai/phone-number/8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e",
    headers={"Authorization": f"Bearer {key}"}
)
p = r2.json()
print(f"Phone: {p.get('number')} -> assistant: {p.get('assistantId', 'none')}")

# Build updated prompt with voice drop campaign knowledge
voice_drop_context = """

=== ACTIVE CAMPAIGN: VOICE DROP FOLLOW-UP ===

IMPORTANT CONTEXT: Dan has sent voice drops and SMS follow-ups to over 1,300 local businesses in the Lakeland, Polk County, and Central Florida area. Many callers may be calling back in response to these messages. Dan is also forwarding his personal phone to this number, so ALL inbound calls come to you.

THE OFFER WE SENT:
- FREE setup of an AI phone answering system
- 2-WEEK FREE TRIAL, no commitment
- The AI answers every call 24/7 so they never miss a customer
- Automatically books appointments
- Gets them more Google & Facebook reviews on autopilot
- Runs automated advertising for their business
- After trial: $297/month

IF SOMEONE CALLS BACK ABOUT THE VOICEMAIL/TEXT:
1. "Hey! Thanks so much for calling back. Yes, that was us! I'm Sarah with AI Service Company."
2. Ask what kind of business they have
3. Ask about their pain points: "When you're busy or on a job, what happens to your phone calls?"
4. Pitch the solution specifically for their industry
5. Emphasize: FREE setup, 2-week trial, no commitment, no risk
6. Close: "We can have your AI agent live within 24 hours. Want to get started?"
7. If yes: Collect their business name, business hours, services, website, and notification phone/email
8. If they want to talk to Dan: "Absolutely! Let me get you scheduled. What time works best?"

BOOKING LINK: https://api.leadconnectorhq.com/widget/booking/sHgMUMdTlRWBFrbpajii

COMMON OBJECTIONS:
- "Is this a scam?" -> "Not at all! We're a local company right here in Central Florida. Dan is the owner. We just want to show you what AI can do for your business - that's why the trial is free."
- "I'm not interested" -> "Totally understand. But quick question - how many calls do you think you miss in a week? Even one missed job pays for this for months. The trial is completely free if you want to just see it work."
- "How does it work?" -> "We set up an AI receptionist with your business name. When someone calls, she answers professionally, collects their info, and books appointments. She sounds like a real person. We can even do a test call right now if you want."
- "What's the catch?" -> "Honestly, no catch. We give you 2 weeks free because we know once you see it working, you'll want to keep it. After the trial it's $297/month and you can cancel anytime."

=== END CAMPAIGN CONTEXT ===
"""

updated_prompt = current_prompt + voice_drop_context

update = {
    "model": {
        "model": d.get("model", {}).get("model", "gpt-4o"),
        "provider": d.get("model", {}).get("provider", "openai"),
        "messages": [{"role": "system", "content": updated_prompt}]
    }
}

r3 = requests.patch(
    "https://api.vapi.ai/assistant/ae717f29-6542-422f-906f-ee7ba6fa0bfe",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json=update
)
print(f"\nSarah voice updated: {r3.status_code}")
if r3.status_code != 200:
    print(r3.text[:300])
else:
    print("Sarah now knows about voice drop campaign and can sell the free trial!")

# Now update the SMS auto-reply via GHL webhook
# We'll set up a webhook handler that auto-replies to inbound texts
GHL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

# Test SMS auto-reply templates
sms_replies = {
    "YES": "Awesome! Thanks for your interest! We'll get your FREE AI phone system set up within 24 hours. Can you reply with your business name and what type of business you run? - Dan, AI Service Company",
    "INTERESTED": "Great to hear! We'd love to get you started with your FREE 2-week trial. Your AI receptionist will answer calls 24/7, book appointments, and get you more reviews. Reply with your business name or call us at (863) 692-8474! - Dan",
    "STOP": "You've been unsubscribed. Sorry for the inconvenience. Reply START if you change your mind.",
    "MORE INFO": "Sure! Our AI phone system answers your business calls 24/7, books appointments, and gets you Google & Facebook reviews on autopilot. FREE setup + 2-week trial, then $297/mo. Want to try it? Call (863) 692-8474 or reply YES! - Dan",
    "HOW MUCH": "The trial is completely FREE for 2 weeks - no commitment. After the trial, it's just $297/month and you can cancel anytime. One missed job pays for it! Want to get started? Reply YES or call (863) 692-8474 - Dan",
    "DEFAULT": "Thanks for reaching out! We're offering local businesses a FREE 2-week trial of our AI phone answering system. It answers calls 24/7, books appointments, and gets you more reviews. Interested? Call us at (863) 692-8474 or reply YES! - Dan"
}

with open("scripts/sms_reply_templates.json", "w") as f:
    json.dump(sms_replies, f, indent=2)
print("\nSMS reply templates saved to scripts/sms_reply_templates.json")
print("Templates: YES, INTERESTED, STOP, MORE INFO, HOW MUCH, DEFAULT")
