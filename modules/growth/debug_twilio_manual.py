from twilio.rest import Client
import sys

# Hardcoded from screenshot/memory
SID = "ACc18098596806342a3047c5b84"
TOKEN = "709de5fed508fdb4fa7fd0a7d92842"
FROM = "+18632608351"
TO = "+13529368152"

print(f"Testing Twilio with Hardcoded Creds:")
print(f"SID: {SID}")
print(f"From: {FROM}")

try:
    client = Client(SID, TOKEN)
    message = client.messages.create(
        body="🦅 Sovereign Stack: Manual Debug Message",
        from_=FROM,
        to=TO
    )
    print(f"✅ SUCCESS! SID: {message.sid}")
except Exception as e:
    print(f"❌ FAILURE: {e}")
