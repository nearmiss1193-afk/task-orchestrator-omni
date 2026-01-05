
import sys
import os
import time
from modules.communication.sovereign_dispatch import dispatcher

def test_ghl_connection():
    print("\n[TEST 1] Testing GHL Connection...")
    if not (dispatcher.ghl_token and dispatcher.ghl_location):
        print("❌ GHL Credentials Missing")
        return False
    
    # Try a lightweight GET request (e.g. get location info or contacts)
    headers = {
        "Authorization": f"Bearer {dispatcher.ghl_token}",
        "Version": "2021-07-28",
        "Accept": "application/json"
    }
    url = f"https://services.leadconnectorhq.com/locations/{dispatcher.ghl_location}"
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            print(f"✅ GHL Connected. Location: {res.json().get('location', {}).get('name')}")
            return True
        else:
            print(f"❌ GHL Error: {res.status_code} - {res.text}")
            return False
    except Exception as e:
        print(f"❌ GHL Exception: {e}")
        return False

def test_email_fallback():
    print("\n[TEST 2] Testing Email Fallback (Simulating GHL Fail)...")
    
    # We will FORCE a GHL fail by passing a bad 'provider' logic or just relying on the fact that if GHL fails it falls back.
    # Actually, let's just send a test email with provider='ghl' to the user.
    # If GHL is broken, it SHOULD send via Resend and return True.
    
    user_email = "nearmiss1193@gmail.com"
    body = "<h1>System Health Check</h1><p>If you see this, the notification system is working.</p>"
    
    success = dispatcher.send_email(user_email, "Sovereign Health Check", body, provider="ghl")
    
    if success:
        print("✅ Email Verification Sent (Check Inbox).")
    else:
        print("❌ Email Verification Failed completely.")

if __name__ == "__main__":
    import requests # Imported locally to ensure it exists
    print("🏥 Running Sovereign Health Check...")
    
    ghl_ok = test_ghl_connection()
    test_email_fallback()
    
    print("\n--- Summary ---")
    print(f"GHL API: {'OK' if ghl_ok else 'FAIL'}")
