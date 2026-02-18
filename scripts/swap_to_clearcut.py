"""Swap Rachel to Clear Cut Tree Masters script and schedule reminder"""
import os, requests, json, time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
load_dotenv(".env")
key = os.environ["VAPI_PRIVATE_KEY"]

prompt = open("scripts/rachel_clearcut_tree.txt", "r").read()

update = {
    "name": "Rachel (Onboarding - Clear Cut Tree Masters)",
    "firstMessage": "Hey! Thanks so much for taking the time to chat with us. I'm Rachel from AI Service Company - I'm going to walk you through exactly what we can do for Clear Cut Tree Masters. This should be fun! How are you doing today?",
    "model": {
        "model": "gpt-4o",
        "provider": "openai",
        "messages": [{"role": "system", "content": prompt}]
    }
}

r = requests.patch(
    "https://api.vapi.ai/assistant/033ec1d3-e17d-4611-a497-b47cab1fdb4e",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    json=update
)
print(f"Rachel updated: {r.status_code}")

# Send reminder text at 3:45 PM
EST = timezone(timedelta(hours=-5))
target = datetime.now(EST).replace(hour=15, minute=45, second=0, microsecond=0)
now = datetime.now(EST)
wait = (target - now).total_seconds()

if wait > 0:
    print(f"Waiting {int(wait)} seconds until 3:45 PM to send reminder...")
    time.sleep(wait)

webhook = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
r2 = requests.post(webhook, json={
    "phone": "+18635832461",
    "message": "Hey! This is Dan from AI Service Company. Just a heads up - your onboarding appointment is coming up at 4:00 PM ET. Rachel, your setup specialist, is standing by at (863) 692-8474. You can call anytime or just reply with a time that works and she will call you! - Dan"
}, timeout=10)
print(f"Reminder sent: {r2.status_code}")
