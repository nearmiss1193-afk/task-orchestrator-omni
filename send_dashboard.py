
from modules.communication.sovereign_dispatch import dispatcher
import time

USER_PHONE = "+13529368152"
DASHBOARD_LINK = "https://aiserviceco.com/dashboard.html"

msg = f"🛡️ Sovereign Command Uplink: {DASHBOARD_LINK}\n\n(Sarah is active and monitoring channels.)"

print(f"🚀 Sending Dashboard Link to {USER_PHONE}...")
try:
    dispatcher.send_sms(USER_PHONE, msg, provider="ghl")
    print("✅ SMS Dispatch Initialized.")
except Exception as e:
    print(f"❌ SMS Failed: {e}")
