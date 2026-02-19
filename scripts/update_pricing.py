"""Update Sarah + SMS templates with corrected pricing: $99/mo, 50% off $49/mo for 3 days"""
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

# Replace old pricing with new
updated = current_prompt.replace("$297/month", "$99/month - and right now we have a 50% off deal at just $49/month for the next 3 days")
updated = updated.replace("$297/mo", "$99/mo (50% off = $49/mo for the next 3 days)")
updated = updated.replace("After trial: $297/month", "After trial: $99/month (50% OFF right now = $49/month if you sign up in the next 3 days!)")

# Also update objection handling
updated = updated.replace(
    "After the trial it's $297/month and you can cancel anytime.",
    "After the trial it's normally $99/month, but right now we're running a 50% off special - just $49/month if you sign up in the next 3 days. And you can cancel anytime."
)

# Add urgency language
if "50% OFF SPECIAL" not in updated:
    urgency = """

=== PRICING & URGENCY ===
CURRENT OFFER (USE THIS IN EVERY PITCH):
- FREE 2-week trial, no commitment
- Normal price: $99/month
- RIGHT NOW: 50% OFF = $49/month (for the next 3 days only!)
- The AI answers calls 24/7, handles conversations intelligently, alerts the owner, and books appointments
- After 3 days, price goes to $99/month

ALWAYS MENTION THE URGENCY: "We're running a 50% off special right now - just $49 a month instead of $99. But that deal ends in 3 days, so if you want to lock it in, now is the time."

If they hesitate: "Look, the trial is free anyway. Try it for 2 weeks, and if you love it, you'll already be locked in at $49/month. That's less than one missed phone call costs your business."
=== END PRICING ===
"""
    updated += urgency

update = {
    "model": {
        "model": d.get("model", {}).get("model", "gpt-4o"),
        "provider": d.get("model", {}).get("provider", "openai"),
        "messages": [{"role": "system", "content": updated}]
    }
}

r2 = requests.patch(
    "https://api.vapi.ai/assistant/ae717f29-6542-422f-906f-ee7ba6fa0bfe",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json=update
)
print(f"Sarah updated: {r2.status_code}")

# Update SMS reply templates
sms_replies = {
    "YES": "Awesome! Let's get you started with your FREE 2-week trial! Plus right now we have a 50% off deal - just $49/mo instead of $99 if you sign up in the next 3 days. Reply with your business name or call (863) 692-8474! - Dan",
    "INTERESTED": "Great! Here's the deal: FREE setup + 2-week trial. Your AI answers calls 24/7, books appointments, and alerts you instantly. Normal price is $99/mo but we're running 50% off right now - just $49/mo for 3 days. Call (863) 692-8474 to get started! - Dan",
    "STOP": "You've been unsubscribed. Sorry for the inconvenience. Reply START if you change your mind.",
    "MORE INFO": "Our AI answers your business calls 24/7, handles conversations like a real person, books appointments, and texts you alerts. FREE 2-week trial, then just $49/mo (50% off for the next 3 days, normally $99). Call (863) 692-8474 or reply YES! - Dan",
    "HOW MUCH": "FREE 2-week trial! After that it's normally $99/mo but we're running 50% off right now - just $49/month. That deal expires in 3 days. One missed call costs more than that! Reply YES or call (863) 692-8474 - Dan",
    "PRICE": "FREE 2-week trial, then just $49/mo (50% off special, normally $99). Answers calls 24/7, books appointments, alerts you. Lock in $49/mo before the deal ends in 3 days! Call (863) 692-8474 - Dan",
    "DEFAULT": "Thanks for reaching out! We're offering a FREE 2-week trial of our AI phone answering system. It answers calls 24/7, handles conversations, books appointments, and alerts you. Right now it's 50% off - just $49/mo (normally $99). Call (863) 692-8474 or reply YES! - Dan"
}

with open("scripts/sms_reply_templates.json", "w") as f:
    json.dump(sms_replies, f, indent=2)
print("SMS templates updated with $99/$49 pricing")

# Also update Rachel
r3 = requests.get(
    "https://api.vapi.ai/assistant/033ec1d3-e17d-4611-a497-b47cab1fdb4e",
    headers={"Authorization": f"Bearer {key}"}
)
rd = r3.json()
rachel_prompt = rd.get("model", {}).get("messages", [{}])[0].get("content", "")
rachel_prompt = rachel_prompt.replace("$297/month", "$99/month (50% off = $49/mo for the next 3 days)")
rachel_prompt = rachel_prompt.replace("$297/mo", "$49/mo (50% off for 3 days, normally $99)")

r4 = requests.patch(
    "https://api.vapi.ai/assistant/033ec1d3-e17d-4611-a497-b47cab1fdb4e",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json={"model": {
        "model": rd.get("model", {}).get("model", "gpt-4o"),
        "provider": rd.get("model", {}).get("provider", "openai"),
        "messages": [{"role": "system", "content": rachel_prompt}]
    }}
)
print(f"Rachel updated: {r4.status_code}")
