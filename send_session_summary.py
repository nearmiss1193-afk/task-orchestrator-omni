"""Send session summary email via GHL webhook"""
import requests

GHL_EMAIL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8"

html = """
<h2>📊 SESSION SUMMARY - 2026-01-13 8:54 PM</h2>

<p><b>Dashboard:</b> <a href="https://www.aiserviceco.com/dashboard.html">aiserviceco.com/dashboard.html</a></p>

<h3>✅ Completed This Session</h3>
<ul>
<li>Created analytics modules: lead_scorer.py, pipeline_analytics.py, ab_test_tracker.py</li>
<li>Created 24/7 Outreach SOP (/outreach_sop) - 15min prospect, 5min calls, timezone-aware</li>
<li>Added Lusha enrichment for direct dial phone/email</li>
<li>Fixed Railway scheduler (error handling to prevent crashes)</li>
<li>Fixed Supabase credential naming (NEXT_PUBLIC_SUPABASE_URL)</li>
<li>Removed 'source' field from leads (column doesn't exist)</li>
<li>Prepared Firebase backup code (needs service account JSON)</li>
</ul>

<h3>🔧 System Status</h3>
<ul>
<li>Railway Worker: ⚠️ <b>Needs redeploy</b></li>
<li>Supabase: ✅ 444 leads in DB</li>
<li>GHL: ✅ 1,777 contacts, SMS active</li>
<li>Sarah AI: ✅ Active (Vapi)</li>
</ul>

<h3>📝 Latest Git Commits</h3>
<pre>
b8ae3d6 💾 SAVE PROTOCOL: Railway fixes, analytics modules, outreach SOP
ada340f fix: Remove 'source' field from leads
20761bb fix: Add error handling to scheduler thread
04689a7 fix: Support both SUPABASE_URL naming conventions
</pre>

<h3>🚀 Recovery Commands</h3>
<pre>
# Check Railway:
curl https://empire-unified-backup-production.up.railway.app/health

# Trigger prospecting:
curl -X POST https://empire-unified-backup-production.up.railway.app/trigger/prospect

# Start local:
cd C:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified
python watchdog.py
</pre>

<h3>⚠️ Next Priority</h3>
<ol>
<li><b>Redeploy Railway</b> - Go to Railway Dashboard > Deployments > Redeploy</li>
<li>After redeploy, trigger prospect and verify stats increase</li>
<li>Get Firebase service account JSON to enable backup</li>
</ol>

<p>- Empire System</p>
"""

print("Sending session summary email...")
r = requests.post(GHL_EMAIL, json={
    "email": "nearmiss1193@gmail.com",
    "from_name": "Empire System",
    "from_email": "system@aiserviceco.com",
    "subject": "📊 SESSION SUMMARY - 2026-01-13 8:54 PM",
    "html_body": html
}, timeout=30)

print(f"Status: {r.status_code}")
print(f"Response: {r.text}")

if r.ok:
    print("✅ Email sent successfully!")
else:
    print("❌ Email failed")
