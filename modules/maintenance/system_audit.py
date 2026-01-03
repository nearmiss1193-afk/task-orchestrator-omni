
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
    "logic_loop": "UNKNOWN",
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

def check_logic_loop():
    print("🔄 Verifying Logic Loop (Test Lead)...")
    if "HEALTHY" not in status_report["database"]:
        status_report["logic_loop"] = "SKIPPED (DB Down)"
        return False

    try:
        # Connect
        result = urllib.parse.urlparse(DATABASE_URL)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        con = pg8000.native.Connection(
            user=result.username, password=result.password, host=result.hostname, port=result.port or 5432, database=result.path[1:], ssl_context=ssl_context
        )

        # 1. Insert Test Lead
        import json
        test_email = "test_audit_bot@aiserviceco.com"
        con.run(
            "INSERT INTO leads (name, email, phone, source, metadata) VALUES (:n, :e, :p, :s, :m)",
            n="Sovereign Audit Bot", e=test_email, p="555-0199", s='SYSTEM_AUDIT', m=json.dumps({"audit": True})
        )
        
        # 2. Verify Insert
        rows = con.run("SELECT email FROM leads WHERE email = :e ORDER BY created_at DESC LIMIT 1", e=test_email)
        if rows and rows[0][0] == test_email:
            status_report["logic_loop"] = "VERIFIED 🟢"
            con.close()
            return True
        else:
            status_report["logic_loop"] = "INSERT FAILED 🔴"
            con.close()
            return False

    except Exception as e:
        status_report["logic_loop"] = f"LOGIC FAIL 🔴 ({str(e)})"
        return False

def send_report():
    print("📧 Dispatching Sovereign Report...")
    if not RESEND_KEY:
        print("❌ No Email Key. Printing Report:")
        print(status_report)
        return

    resend.api_key = RESEND_KEY
    
    is_healthy = "🟢" if "VERIFIED" in status_report["logic_loop"] else "⚠️"
    
    html_body = f"""
    <h1>Sovereign System Audit {is_healthy}</h1>
    <p><strong>System Status:</strong> {is_healthy}</p>
    <hr>
    <ul>
        <li><strong>Database:</strong> {status_report['database']}</li>
        <li><strong>Stripe API:</strong> {status_report['stripe']}</li>
        <li><strong>Logic Loop (Test Lead):</strong> {status_report['logic_loop']}</li>
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
    
    check_database()
    check_stripe()
    check_logic_loop()
    
    send_report()
