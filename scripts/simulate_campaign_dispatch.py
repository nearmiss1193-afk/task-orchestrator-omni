
import os
import time

# Target Email (from env or fallback)
TARGET_EMAIL = os.environ.get("GHL_EMAIL", "USER_EMAIL_NOT_SET")

CAMPAIGNS = [
    {
        "niche": "HVAC",
        "subject": "missed calls cost you $15k last month (fix inside)",
        "body": "Hey,\nI audited your area and noticed your ads... \n\nLink: http://localhost:3000/landing/hvac.html"
    },
    {
        "niche": "Plumber",
        "subject": "emergency dispatch (automated)",
        "body": "When a pipe bursts, speed is everything... \n\nLink: http://localhost:3000/landing/plumber.html"
    },
    {
        "niche": "Roofer",
        "subject": "scaling for the next hail storm?",
        "body": "When the storm hits, your phone lines get flooded... \n\nLink: http://localhost:3000/landing/roofer.html"
    },
    {
        "niche": "Electrician",
        "subject": "re: panel upgrades",
        "body": "High-margin jobs like panel upgrades often get lost... \n\nLink: http://localhost:3000/landing/electrician.html"
    },
    {
        "niche": "Solar",
        "subject": "650+ credit score leads only",
        "body": "Solar is a numbers game... \n\nLink: http://localhost:3000/landing/solar.html"
    },
    {
        "niche": "Landscaping",
        "subject": "recurring revenue automation",
        "body": "Are you bogged down scheduling $50 mows? \n\nLink: http://localhost:3000/landing/landscaping.html"
    },
    {
        "niche": "Pest Control",
        "subject": "locking in quarterly contracts",
        "body": "One-off sprays are fine, but recurring plans build empires... \n\nLink: http://localhost:3000/landing/pest.html"
    },
    {
        "niche": "Cleaning",
        "subject": "filling hour gaps in your schedule",
        "body": "Empty slots in your cleaners' schedules are burning cash... \n\nLink: http://localhost:3000/landing/cleaning.html"
    },
    {
        "niche": "Restoration",
        "subject": "insurance claim leads (speed matters)",
        "body": "In restoration, if you aren't first, you're last... \n\nLink: http://localhost:3000/landing/restoration.html"
    },
    {
        "niche": "Auto Detail",
        "subject": "booking more ceramic coatings",
        "body": "A $50 wash is work. A $900 ceramic coating is profit... \n\nLink: http://localhost:3000/landing/autodetail.html"
    }
]

LOG_FILE = "campaign_simulation_log.txt"

print(f"🚀 Simulating Dispatch of 10 Camapign Emails to {TARGET_EMAIL}...\n")

with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"TIMESTAMP: {time.ctime()}\n")
    f.write(f"TARGET: {TARGET_EMAIL}\n")
    f.write("-" * 40 + "\n")
    
    for camp in CAMPAIGNS:
        print(f"   Sending to {camp['niche']}...", end=" ")
        time.sleep(0.5) # Simulate network delay
        
        entry = f"""
[EMAIL SENT]
To: {TARGET_EMAIL}
Subject: {camp['subject']}
----------------------------------------
{camp['body']}
----------------------------------------
[STATUS: 200 OK (Simulated)]
        """
        f.write(entry + "\n\n")
        print("✅ SENT")

print(f"\n✨ Simulation Complete. Log saved to {LOG_FILE}")
