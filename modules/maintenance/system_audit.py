
import os
import requests
import stripe
import pg8000.native
import ssl
import urllib.parse
from dotenv import load_dotenv
import resend

load_dotenv()

# --- CONFIG ---
STRIPE_KEY = os.getenv("STRIPE_SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
RESEND_KEY = os.getenv("RESEND_API_KEY")
OWNER_EMAIL = "nearmiss1193@gmail.com"

# --- STATUS TRACKER ---
status_report = {
    "database": "UNKNOWN",
    "stripe": "UNKNOWN",
    "email": "UNKNOWN",
    "overall": "UNKNOWN"
}

def check_database():
    print("🩺 Checking Database Heartbeat...")
    if not DATABASE_URL:
        status_report["database"] = "MISSING_URL"
        return False
    
    try:
        result = urllib.parse.urlparse(DATABASE_URL)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        con = pg8000.native.Connection(
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432,
            database=result.path[1:],
            ssl_context=ssl_context
        )
        con.run("SELECT 1")
        con.close()
        status_report["database"] = "HEALTHY 🟢"
        return True
    except Exception as e:
        status_report["database"] = f"CRITICAL FAILURE 🔴 ({str(e)})"
        return False

def check_stripe():
    print("💳 Checking Stripe Connection...")
    if not STRIPE_KEY:
        status_report["stripe"] = "MISSING_KEY"
        return False
    
    stripe.api_key = STRIPE_KEY
    try:
        stripe.Balance.retrieve()
        status_report["stripe"] = "CONNECTED 🟢"
        return True
    except Exception as e:
        status_report["stripe"] = f"API FAIL 🔴 ({str(e)})"
        return False

def send_report():
    print("📧 Dispatching Sovereign Report...")
    if not RESEND_KEY:
        print("❌ No Email Key. Printing Report:")
        print(status_report)
        return

    resend.api_key = RESEND_KEY
    
    is_healthy = "🟢" if "HEALTHY" in status_report["database"] and "CONNECTED" in status_report["stripe"] else "⚠️"
    
    html_body = f"""
    <h1>Sovereign System Audit {is_healthy}</h1>
    <p><strong>System Status:</strong> {is_healthy}</p>
    <hr>
    <ul>
        <li><strong>Database:</strong> {status_report['database']}</li>
        <li><strong>Stripe API:</strong> {status_report['stripe']}</li>
        <li><strong>Email Gateway:</strong> CONNECTED 🟢</li>
    </ul>
    <hr>
    <p><em>Heartbeat 2.0 Auto-Diagnostic</em></p>
    """
    
    try:
        resend.Emails.send({
            "from": "alert@aiserviceco.com",
            "to": [OWNER_EMAIL],
            "subject": f"System Sovereign: {is_healthy} Audit Report",
            "html": html_body
        })
        print("✅ Report Sent.")
    except Exception as e:
        print(f"❌ Email Failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Heartbeat 2.0 Audit...")
    
    db_ok = check_database()
    str_ok = check_stripe()
    
    send_report()
