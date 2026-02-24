import asyncio
from workers.email_triage import handle_inbound_email

print("TESTING TRIAGE ENGINE (GHL WEBHOOK OVERRIDE)")
result = handle_inbound_email(
    "dan@aiserviceco.com", 
    "Meeting Request", 
    "Hey Sarah, this looks great. Do you have a calendar link for Dan? I want to book a call."
)
print("TRIAGE OUTPUT:", result)
