import os
import sys

# Add root to sys.path to find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.communication.sovereign_dispatch import dispatcher
except ImportError:
    print("❌ Could not import SovereignDispatch.")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv()

TARGET_EMAIL = os.environ.get("GHL_EMAIL")
REPORT_FILE = "full_status_report.md"

def send_ghl_report():
    print(f"📧 Initiating GHL Protocol to {TARGET_EMAIL}...")
    
    if not TARGET_EMAIL:
        print("❌ Missing GHL_EMAIL env var.")
        return

    # Read Report
    try:
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            report_content = f.read()
    except Exception as e:
        print(f"❌ File Read Error: {e}")
        return

    # Use HTML for better formatting in GHL
    html_body = f"<html><body><pre style='font-family: monospace; whitespace: pre-wrap;'>{report_content}</pre></body></html>"
    subject = "🛡️ SAVE PROTOCOL: Full Status Report"

    # Send via Dispatcher (GHL Mode)
    # This automatically handles contact lookup and auth
    success = dispatcher.send_email(TARGET_EMAIL, subject, html_body, provider="ghl")
    
    if success:
        print("✅ Report Sent Successfully via GHL!")
    else:
        print("❌ Report Failed. Check logs above.")

if __name__ == "__main__":
    send_ghl_report()
