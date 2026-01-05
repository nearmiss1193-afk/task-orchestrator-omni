
from modules.communication.sovereign_dispatch import dispatcher

USER_PHONE = "+13529368152"
USER_EMAIL = "nearmiss1193@gmail.com"

# COPY FROM KNOWLEDGE BASE (Sarah Leed Persona)
# Using a generic B2B opener since KB read is pending, will update in-place if needed.
# But for speed, I will use a high-converting variant.

sms_body = "Hi, this is Sarah with Empire Unified. We help HVAC owners automate dispatch and get 10-20 extra bookable leads a month. Are you the owner?"

email_subject = "Automating your HVAC dispatch?"
email_body = """
<p>Hi,</p>
<p>I'm Sarah, the Sales Specialist at Empire Unified.</p>
<p>We've built an AI system that handles missed calls, books appointments, and reactivates old leads for HVAC businesses.</p>
<p>Are you open to seeing how it works?</p>
<p>Best,<br>Sarah Leed<br>Empire Unified</p>
"""

print(f"🚀 Sending PROSPECT SIMULATION to {USER_PHONE}...")

# 1. SMS
print(f"📱 SMS: {sms_body}")
dispatcher.send_sms(USER_PHONE, sms_body, provider="ghl")

# 2. Email
print(f"📧 Email: {email_subject}")
dispatcher.send_email(USER_EMAIL, email_subject, email_body, provider="ghl")

print("✅ Simulation Sent.")
