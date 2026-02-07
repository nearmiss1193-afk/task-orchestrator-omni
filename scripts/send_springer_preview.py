"""Send Springer Bros Preview Email via Resend API with Attachments"""
import os
import sys
import base64
from dotenv import load_dotenv
import resend

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

html = '''
<html>
<head>
<style>
  body { font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; padding: 20px; }
  .status-green { color: #22c55e; font-weight: bold; }
  .status-red { color: #ef4444; font-weight: bold; }
  .status-yellow { color: #f59e0b; font-weight: bold; }
  table { width: 100%; border-collapse: collapse; margin: 15px 0; }
  th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
  th { background-color: #f5f5f5; }
  .cta-btn { background-color: #2563eb; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 15px 0; }
  .risk-box { background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 15px 0; }
  .offer-box { background-color: #dcfce7; border-left: 4px solid #22c55e; padding: 15px; margin: 15px 0; }
</style>
</head>
<body>

<p>Hey Derek,</p>

<p>I'm Dan Coffman, a digital strategist here in Lakeland. I visited Springer Bros' website today and ran a technical audit while reviewing your team's services. I found a couple things you'll want to know about:</p>

<h3>🔍 Quick Audit Results</h3>
<table>
  <tr><th>Area</th><th>Status</th><th>Finding</th></tr>
  <tr>
    <td><strong>Legal Compliance</strong></td>
    <td><span class="status-red">🔴 CRITICAL</span></td>
    <td>Missing Terms of Service page</td>
  </tr>
  <tr>
    <td><strong>Mobile Speed</strong></td>
    <td><span class="status-yellow">🟡 WARNING</span></td>
    <td>Score: 79/100 (average)</td>
  </tr>
  <tr>
    <td><strong>After-Hours Capture</strong></td>
    <td><span class="status-green">🟢 OPPORTUNITY</span></td>
    <td>Grow revenue with 24/7 lead intake</td>
  </tr>
</table>

<div class="risk-box">
<strong>⚠️ The Legal Issue</strong><br>
Florida has seen a surge of ADA/website compliance lawsuits. The average settlement in Florida is <strong>$25,000</strong>, with Tampa-area cases averaging <strong>$59,000</strong>. Without a Terms of Service page, your site could be an easy target for "drive-by" lawyers.
</div>

<h3>📊 What These Mean</h3>
<p><strong>Missing Terms of Service:</strong> This is a legal liability. A Terms of Service page protects you from frivolous lawsuits and clearly states your service boundaries. Takes 30 minutes to fix.</p>

<p><strong>Mobile Speed 79/100:</strong> Not terrible, but Google penalizes sites under 90. Your competitors with faster sites are appearing higher in "AC repair Lakeland" searches. (See attached PageSpeed report)</p>

<p><strong>After-Hours Leads:</strong> When customers call at 9PM with a broken AC, what happens? An AI voice assistant can capture those emergency leads 24/7 while you sleep - this is a growth opportunity, not a problem.</p>

<div class="offer-box">
<strong>✅ My Offer (No Strings)</strong><br>
<ol>
<li><strong>Free Terms of Service Page</strong> - I'll draft and implement one for your site this week, at no cost</li>
<li><strong>14-Day AI Receptionist Trial</strong> - Answers calls 24/7, books appointments, never gets tired</li>
</ol>
</div>

<p>I'm in Lakeland too (moved here in 2018), so proving my value to local businesses is important to me. The Terms of Service fix is completely free - I want to earn your trust before asking for anything.</p>

<p>Worth a 10-minute call to discuss? Reply here or call me directly.</p>

<p>
<strong>Daniel Coffman</strong><br>
📞 352-936-8152<br>
Owner, AI Service Co<br>
🌐 <a href="https://www.aiserviceco.com">www.aiserviceco.com</a>
</p>

<p style="color: #888; font-size: 12px; margin-top: 30px;">
P.S. I've attached a screenshot of your PageSpeed report for your records.
</p>

</body>
</html>
'''

if not resend.api_key:
    print("❌ RESEND_API_KEY not found!")
    sys.exit(1)

print("Sending Springer Bros preview via Resend with attachment...")

# Find and attach PageSpeed screenshot
attachments = []
screenshot_paths = [
    "audit_screenshots/Springer_Bros_slow_load.png",
    "C:/Users/nearm/.gemini/antigravity/brain/0b97dae9-c5c0-4924-8d97-793b59319985/springer_pagespeed.png"
]

for path in screenshot_paths:
    if os.path.exists(path):
        print(f"   Found attachment: {path}")
        with open(path, "rb") as f:
            content = base64.standard_b64encode(f.read()).decode("utf-8")
        attachments.append({
            "filename": "PageSpeed_Report.png",
            "content": content
        })
        break
else:
    print("   ⚠️ No PageSpeed screenshot found, sending without attachment")

try:
    params = {
        "from": "Dan Coffman <dan@aiserviceco.com>",
        "to": "nearmiss1193@gmail.com",
        "subject": "[PREVIEW] Found 2 issues on your website, Derek (one could cost $25K+)",
        "html": html,
        "text": "Hey Derek, I ran a technical audit on Springer Bros' website and found some issues. Please view the HTML version for the full report."
    }
    if attachments:
        params["attachments"] = attachments
    
    r = resend.Emails.send(params)
    print(f"✅ Email sent! ID: {r['id']}")
except Exception as e:
    print(f"❌ Failed: {e}")
