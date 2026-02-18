"""Send Tiffany a reminder at 2:00 PM ET about her 2:30 PM appointment"""
import time, requests
from datetime import datetime, timezone, timedelta

EST = timezone(timedelta(hours=-5))
target = datetime.now(EST).replace(hour=14, minute=0, second=0, microsecond=0)
now = datetime.now(EST)
wait = (target - now).total_seconds()

if wait > 0:
    print(f"Waiting {int(wait)} seconds until 2:00 PM ET...")
    time.sleep(wait)

print(f"Sending SMS at {datetime.now(EST).strftime('%I:%M %p')} ET...")
webhook = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
r = requests.post(webhook, json={
    "phone": "+13524349704",
    "message": "Hi Tiffany! Just a friendly reminder - your onboarding appointment with AI Service Company is in 30 minutes at 2:30 PM ET. We're excited to get your AI office agent set up for Embracing Concepts! Talk soon. - Dan"
}, timeout=10)
print(f"SMS sent: {r.status_code}")
print(r.text[:200])
