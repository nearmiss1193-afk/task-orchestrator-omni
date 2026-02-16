#!/usr/bin/env python3
"""
Save Protocol Email Notification
Sends recovery protocol email to stakeholders after save.
"""
import os
import sys
import json
from datetime import datetime

# Read RESEND_API_KEY from .env with robust handling
RESEND_KEY = None
try:
    with open('.env', 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line.startswith('RESEND_API_KEY='):
                RESEND_KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
                break
except Exception as e:
    print(f"Warning: Could not read .env: {e}")

if not RESEND_KEY:
    print("❌ RESEND_API_KEY not found - email notification skipped")
    sys.exit(0)  # Don't fail the save protocol

print(f"📧 Preparing Save Protocol Notification...")
print(f"   API Key: {RESEND_KEY[:10]}...")

import requests

# Read Gaps Document
gaps_content = ""
try:
    gaps_path = 'knowledge_base/CAPABILITIES_GAPS.md'
    if os.path.exists(gaps_path):
        with open(gaps_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Simple Markdown Table to HTML conversion
            in_table = False
            html_table = '<table style="width:100%; border-collapse: collapse; margin-top: 10px; color: #eee; font-size: 13px;">'
            for line in lines:
                line = line.strip()
                if line.startswith('|'):
                    in_table = True
                    cells = [c.strip() for c in line.split('|')[1:-1]]
                    if not all(c == '-' or c.startswith('---') for c in cells):
                        html_table += '<tr>'
                        for cell in cells:
                            style = "border: 1px solid #333; padding: 8px;"
                            if '✅' in cell: cell = f'<span style="color: #00ff88;">{cell}</span>'
                            if '🔴' in cell: cell = f'<span style="color: #ff4d4d;">{cell}</span>'
                            html_table += f'<td style="{style}">{cell}</td>'
                        html_table += '</tr>'
                elif in_table:
                    html_table += '</table>'
                    gaps_content += html_table + "<br>"
                    html_table = '<table style="width:100%; border-collapse: collapse; margin-top: 10px; color: #eee; font-size: 13px;">'
                    in_table = False
                elif line.startswith('##'):
                    gaps_content += f'<h3 style="color: #00d9ff; margin-top: 20px;">{line.replace("##", "").strip()}</h3>'
                elif line.startswith('#'):
                    continue
                elif line:
                    gaps_content += f'<p style="color: #aaa;">{line}</p>'
            if in_table:
                html_table += '</table>'
                gaps_content += html_table
    else:
        gaps_content = "<p style='color: #ff4d4d;'>⚠️ CAPABILITIES_GAPS.md not found.</p>"
except Exception as e:
    gaps_content = f"<p style='color: #ff4d4d;'>⚠️ Error reading gaps: {e}</p>"

# Email Body
timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
email_body = f"""
<html>
<body style="font-family: Arial, sans-serif; background: #1a1a2e; color: #eee; padding: 20px;">
    <div style="max-width: 700px; margin: 0 auto; background: #16213e; padding: 30px; border-radius: 10px; border: 1px solid #00d9ff;">
        <h1 style="color: #00d9ff; text-align: center;">💾 Sovereign Save Protocol</h1>
        <p style="color: #aaa; text-align: center;">Operational Snapshot: {timestamp}</p>
        
        <hr style="border-color: #333; margin: 20px 0;">
        
        <h2 style="color: #00ff88;">📊 System Capabilities & Gaps</h2>
        {gaps_content}
        
        <hr style="border-color: #333; margin: 20px 0;">
        
        <h2 style="color: #00ff88;">✅ Today's Core Updates</h2>
        <ul>
            <li><b>Phase 14 Logic</b>: Consolidation of Heartbeat + Outreach into Nexus pulse.</li>
            <li><b>Weekly Digest</b>: Newsletter engine implemented & scheduled.</li>
            <li><b>Ayrshare Integrated</b>: Multi-channel social broadcast enabled.</li>
        </ul>
        
        <h2 style="color: #ffa500;">📋 Quick Recovery</h2>
        <pre style="background: #0d1117; padding: 15px; border-radius: 5px; color: #58a6ff; font-size: 12px;">
cd C:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified
git pull origin main
vercel deploy --prod
python -m modal deploy deploy.py
        </pre>
        
        <hr style="border-color: #333;">
        <p style="color: #666; font-size: 12px; text-align: center;">
            AI Service Co | Sovereign Intelligence Network<br>
            <a href="https://www.aiserviceco.com" style="color: #00d9ff; text-decoration: none;">www.aiserviceco.com</a>
        </p>
    </div>
</body>
</html>
"""

# Send via Resend API
recipients = ["nearmiss1193@gmail.com", "owner@aiserviceco.com"]

try:
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": "Empire System <alert@aiserviceco.com>",
            "to": recipients,
            "subject": f"💾 Save Protocol Complete - {timestamp}",
            "html": email_body
        }
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"✅ Email sent to {recipients}")
        print(f"   ID: {data.get('id', 'unknown')}")
    else:
        print(f"❌ Email failed: {response.status_code}")
        print(f"   {response.text[:200]}")
except Exception as e:
    print(f"❌ Email error: {e}")
