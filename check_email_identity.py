
import os
import sys
from modules.email_command import EmailCommander

def check_identity():
    print("🕵️ Checking Gmail Identity...")
    try:
        commander = EmailCommander()
        if not commander.service:
            print("❌ Service not authenticated.")
            return

        profile = commander.service.users().getProfile(userId='me').execute()
        email = profile.get('emailAddress')
        print(f"✅ Authenticated as: {email}")
    except Exception as e:
        print(f"❌ Error checking identity: {e}")

if __name__ == "__main__":
    check_identity()
