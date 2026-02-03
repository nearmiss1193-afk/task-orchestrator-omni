
import os
import sys

# Allow import from sibling module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from communication.sovereign_dispatch import dispatcher

# Configuration
TO_EMAIL = "nearmiss1193@gmail.com"
TO_PHONE = "+13526453244"
DOMAIN = "https://aiserviceco.com"

# The Link Map based on verified public/ directory
PAGES = [
    {"name": "⚡ Nexus Hub (Home)", "url": f"{DOMAIN}/"},
    {"name": "📊 Warlord Dashboard", "url": f"{DOMAIN}/dashboard.html"},
    {"name": "❄️ HVAC & Climate", "url": f"{DOMAIN}/hvac.html"},
    {"name": "💧 Plumber", "url": f"{DOMAIN}/plumber.html"},
    {"name": "🏠 Roofer", "url": f"{DOMAIN}/roofer.html"},
    {"name": "⚡ Electrician", "url": f"{DOMAIN}/electrician.html"},
    {"name": "☀️ Solar", "url": f"{DOMAIN}/solar.html"},
    {"name": "🌿 Landscaping", "url": f"{DOMAIN}/landscaping.html"},
    {"name": "🐜 Pest Control", "url": f"{DOMAIN}/pest.html"},
    {"name": "🌊 Restoration", "url": f"{DOMAIN}/restoration.html"},
    {"name": "🚗 Auto Detail", "url": f"{DOMAIN}/autodetail.html"},
    {"name": "✨ Cleaning", "url": f"{DOMAIN}/cleaning.html"},
    {"name": "🔍 Audit Tool", "url": f"{DOMAIN}/audit.html"},
    {"name": "📅 Booking Flow", "url": f"{DOMAIN}/booking.html"}
]

def send_site_map():
    print("🗺️ Generating Sovereign Site Map...")
    
    html_body = "<h2>🦅 Empire Sovereign Cloud - Link Map</h2>"
    html_body += "<p>All systems operational. Click to verify deployment.</p>"
    html_body += "<ul>"
    
    sms_body = "🦅 Sovereign Link Map:\n"
    
    for page in PAGES:
        html_body += f"<li style='margin-bottom: 10px;'><a href='{page['url']}'><strong>{page['name']}</strong></a><br><span style='font-size: 12px; color: #666;'>{page['url']}</span></li>"
        if "Nexus" in page['name'] or "Dashboard" in page['name'] or "HVAC" in page['name']:
             sms_body += f"{page['name']}: {page['url']}\n"
    
    html_body += "</ul>"
    html_body += "<hr><p><em>Deployed via Sovereign Save Protocol</em></p>"

    # 1. SEND EMAIL
    print(f"📨 Dispatching Map to {TO_EMAIL}...")
    try:
        dispatcher.send_email(
            to_email=TO_EMAIL,
            subject="🦅 Sovereign Link Map: All Systems Go",
            html_body=html_body
        )
        print("✅ EMAIL SENT.")
    except Exception as e:
        print(f"❌ EMAIL FAILED: {e}")

    # 2. SEND SMS
    print(f"📱 Dispatching Map to {TO_PHONE}...")
    try:
        dispatcher.send_sms(
            to_phone=TO_PHONE,
            body=sms_body
        )
        print("✅ SMS SENT.")
    except Exception as e:
        print(f"❌ SMS FAILED: {e}")

if __name__ == "__main__":
    send_site_map()
