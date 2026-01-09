# send_sms_twilio.py
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

SID = os.getenv("TWILIO_ACCOUNT_SID")
TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TO_NUMBER = os.getenv("TEST_PHONE") # Using Test Phone (+1352...) from env

client = Client(SID, TOKEN)

print(f"Sending via Twilio: {FROM_NUMBER} -> {TO_NUMBER}")

msg = client.messages.create(
    body="Hey, this is John from the roofing team. My other line is acting up. Just sent you an email with that estimate link.",
    from_=FROM_NUMBER,
    to=TO_NUMBER
)

print(f"Sent! SID: {msg.sid}")
print(f"Status: {msg.status}")
