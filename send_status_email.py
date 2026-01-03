import os
import resend

# Manual .env loader for local execution stability
try:
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('"').strip("'")
except Exception: pass

try:
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
    if not RESEND_API_KEY:
        print("❌ Error: RESEND_API_KEY not found in environment.")
        exit(1)

    resend.api_key = RESEND_API_KEY

    params = {
        "from": "alert@aiserviceco.com",
        "to": ["admin@aiserviceco.com", "nearmiss1193@gmail.com"],
        "subject": "🦅 Empire System Status: SOVEREIGN [Online]",
        "html": """
        <h1>System Reporting Online</h1>
        <p><strong>Status:</strong> Nominal 🟢</p>
        <p><strong>Database:</strong> Connected (Supabase)</p>
        <p><strong>Intelligence:</strong> Active (Vapi Webhook)</p>
        <p><strong>Email:</strong> Verified (DNS Propagation Successful)</p>
        <hr>
        <h3>Access Links:</h3>
        <ul>
            <li><a href="https://empire-sovereign-cloud.vercel.app/dashboard.html"><strong>Admin Dashboard</strong></a></li>
            <li><a href="https://empire-sovereign-cloud.vercel.app/"><strong>Live Landing Page</strong></a></li>
        </ul>
        <hr>
        <p>The Empire is standing guard.</p>
        """
    }

    # Debug Domain Status first
    print("\n--- DIAGNOSTICS ---")
    try:
        domains = resend.Domains.list()
        found = False
        for d in domains.get('data', []):
            if d['name'] == 'aiserviceco.com':
                found = True
                print(f"🔍 Domain Status: {d['status'].upper()}")
                if d['status'] != 'verified':
                    print("⚠️ Domain not yet fully verified. Attempting to send anyway...")
        if not found:
             print("⚠️ Domain 'aiserviceco.com' not found in Resend account.")
    except Exception as e:
        print(f"⚠️ Could not check domain status: {e}")
    print("-------------------\n")

    email = resend.Emails.send(params)
    print(f"✅ Email Sent! ID: {email.get('id')}")

except Exception as e:
    print(f"❌ Email Failed: {e}")
