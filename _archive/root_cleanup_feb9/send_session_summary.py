"""Send session summary email via GHL webhook"""
import os, requests, json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8"

summary = f"""
📊 SESSION SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Completed:**
- ✅ Deployed GHL embeds to contact section (form + calendar)
- ✅ Removed sovAuditForm, Calendly, formsubmit.co
- ✅ Fixed Sarah button - async SDK load + assistant ID
- ✅ Upgraded Vapi widget from 50px to 200px full widget
- ✅ Added BOARD LOCK V1 (3/4 consensus required)
- ✅ Added BOARD OVERRIDE V2 (no self-fix on board calls)
- ✅ Ran board calls with raw API output (Claude, Grok, Gemini, ChatGPT)

**Git Commits:**
- 7ecaaff - GHL embeds deployed
- 845727e - BOARD LOCK V1
- 94b4d4d - BOARD OVERRIDE V2
- c852e7e - Sarah button fix
- ed1afb7 - Full widget upgrade
- 893346a - SAVE PROTOCOL

**Active Systems:**
- Campaign Status: Working
- Sarah AI: full_widget_v1 (200px)
- Modal Cloud: ✅
- GHL Integration: ✅ (form: RnK4OjX0oDcqtWw0VyLr)
- Supabase: ✅

**Dashboard:** https://www.aiserviceco.com/dashboard.html

**Recovery Command:**
cd C:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified
python watchdog.py

**Next Priority:**
1. Verify live site - GHL form + calendar rendering
2. Test Sarah call button - should start call without alert
3. Resume outreach campaigns
"""

payload = {
    "to": "nearmiss1193@gmail.com",
    "subject": f"🤖 Session Summary - {datetime.now().strftime('%Y-%m-%d')}",
    "message": summary
}

print("Sending session summary email...")
try:
    r = requests.post(GHL_EMAIL_WEBHOOK, json=payload, timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")
