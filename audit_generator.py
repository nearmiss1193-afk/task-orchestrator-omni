"""
SELF-HOSTED AUDIT REPORT GENERATOR
Like Manus - creates unique HTML report pages for each prospect
"""
import os
import json
import time
import re
import uuid
from datetime import datetime

# Report storage directory
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "public", "audits")
BASE_URL = "https://www.aiserviceco.com/audits"

def ensure_reports_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_report_html(company_name, website, audit_data):
    """Generate a standalone HTML audit report"""
    
    report_id = str(uuid.uuid4())[:8]
    filename = f"{company_name.lower().replace(' ', '-')}-{report_id}.html"
    
    # Extract audit data
    load_time = audit_data.get('load_time', 'N/A')
    widgets = audit_data.get('widgets', [])
    phones = audit_data.get('phones', [])
    office_stack = audit_data.get('office_stack', {})
    financials = audit_data.get('financials', {})
    
    missed_revenue = financials.get('missed_revenue_annual', 0)
    office_waste = financials.get('office_waste_annual', 0)
    total_opportunity = financials.get('total_opportunity', missed_revenue + office_waste)
    
    # Status indicators
    chat_status = "✅ Found" if widgets else "❌ Missing"
    chat_class = "status-good" if widgets else "status-bad"
    
    booking_status = office_stack.get('booking', 'Manual')
    booking_class = "status-good" if "Automated" in booking_status else "status-bad"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Audit: {company_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            padding: 40px 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            margin-bottom: 30px;
        }}
        .logo {{
            font-size: 24px;
            color: #00d4ff;
            margin-bottom: 20px;
        }}
        h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}
        .company-name {{
            color: #00d4ff;
            font-size: 28px;
        }}
        .hero-stat {{
            background: linear-gradient(135deg, #ff4b4b 0%, #ff6b6b 100%);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .hero-stat h2 {{
            font-size: 48px;
            margin-bottom: 10px;
        }}
        .hero-stat p {{
            font-size: 18px;
            opacity: 0.9;
        }}
        .card {{
            background: rgba(255,255,255,0.08);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
        }}
        .card h3 {{
            font-size: 20px;
            margin-bottom: 15px;
            color: #00d4ff;
        }}
        .status-row {{
            display: flex;
            justify-content: space-between;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .status-row:last-child {{
            border-bottom: none;
        }}
        .status-good {{ color: #00ff88; }}
        .status-bad {{ color: #ff4b4b; }}
        .status-warn {{ color: #ffaa00; }}
        .cta {{
            background: linear-gradient(135deg, #00d4ff 0%, #0088ff 100%);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-top: 30px;
        }}
        .cta h3 {{
            font-size: 24px;
            margin-bottom: 15px;
        }}
        .cta-btn {{
            display: inline-block;
            background: #fff;
            color: #0088ff;
            padding: 15px 40px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: bold;
            font-size: 18px;
            margin: 10px;
        }}
        .cta-btn:hover {{
            transform: scale(1.05);
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            opacity: 0.7;
            font-size: 14px;
        }}
        .breakdown {{
            margin-top: 15px;
        }}
        .breakdown-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🔍 AI Service Co | Website Audit</div>
            <h1>Audit Report for</h1>
            <div class="company-name">{company_name}</div>
            <p style="margin-top: 15px; opacity: 0.7;">Generated {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        
        <div class="hero-stat">
            <h2>${total_opportunity:,}</h2>
            <p>Estimated Annual Revenue Loss</p>
        </div>
        
        <div class="card">
            <h3>📊 Key Findings</h3>
            <div class="status-row">
                <span>AI Chat Widget</span>
                <span class="{chat_class}">{chat_status}</span>
            </div>
            <div class="status-row">
                <span>Online Booking</span>
                <span class="{booking_class}">{booking_status}</span>
            </div>
            <div class="status-row">
                <span>Page Load Time</span>
                <span class="{"status-good" if float(str(load_time).replace("N/A", "5")) < 3 else "status-warn"}">{load_time}s</span>
            </div>
            <div class="status-row">
                <span>Phone Numbers Found</span>
                <span>{len(phones)} number(s)</span>
            </div>
        </div>
        
        <div class="card">
            <h3>💰 Revenue Impact Breakdown</h3>
            <div class="breakdown">
                <div class="breakdown-item">
                    <span>Missed Calls (No AI Receptionist)</span>
                    <span class="status-bad">${missed_revenue:,}/year</span>
                </div>
                <div class="breakdown-item">
                    <span>Manual Scheduling Waste</span>
                    <span class="status-warn">${office_waste:,}/year</span>
                </div>
                <div class="breakdown-item" style="font-weight: bold; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.2);">
                    <span>Total Opportunity</span>
                    <span class="status-bad">${total_opportunity:,}/year</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>🎯 Recommendations</h3>
            <ul style="list-style: none; padding: 0;">
                {"<li style='padding: 10px 0;'>❌ <strong>Add AI Chat Widget</strong> - Capture leads 24/7 even when you're busy</li>" if not widgets else "<li style='padding: 10px 0;'>✅ Chat widget detected</li>"}
                {"<li style='padding: 10px 0;'>❌ <strong>Automate Booking</strong> - Let customers book appointments instantly</li>" if "Manual" in booking_status else "<li style='padding: 10px 0;'>✅ Online booking available</li>"}
                <li style='padding: 10px 0;'>📞 <strong>AI Receptionist</strong> - Never miss a call, even after hours</li>
                <li style='padding: 10px 0;'>📱 <strong>SMS Auto-Reply</strong> - Respond to texts in seconds</li>
            </ul>
        </div>
        
        <div class="cta">
            <h3>Ready to Stop Losing ${int(total_opportunity/12):,}/month?</h3>
            <p style="margin-bottom: 20px;">Get a free 15-minute demo of our AI automation</p>
            <a href="tel:+13527585336" class="cta-btn">📞 Call Now</a>
            <a href="sms:+13527585336?body=Hi! I just saw my website audit and I'm interested." class="cta-btn">💬 Text Us</a>
        </div>
        
        <div class="footer">
            <p>AI Service Co | Automating Local Businesses</p>
            <p>Questions? Call (352) 758-5336</p>
        </div>
    </div>
</body>
</html>
'''
    
    # Save the file
    ensure_reports_dir()
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    report_url = f"{BASE_URL}/{filename}"
    print(f"   📄 Report generated: {report_url}")
    
    return report_url, filepath

def generate_quick_audit(company_name, website=None):
    """Generate audit without Playwright (faster, for leads without websites)"""
    # Default audit assuming no AI tools
    audit_data = {
        'load_time': 'N/A',
        'widgets': [],
        'phones': [],
        'office_stack': {
            'booking': 'Manual (Phone/Form)',
            'payroll': 'Likely Manual',
            'inefficiency_score': 'High'
        },
        'financials': {
            'missed_revenue_annual': 144000,
            'office_waste_annual': 15600,
            'total_opportunity': 159600
        }
    }
    
    return generate_report_html(company_name, website or "", audit_data)


if __name__ == "__main__":
    # Test - generate a sample report
    print("🔧 Testing Audit Report Generator...")
    
    url, path = generate_quick_audit("ProCare Lakeland HVAC", "https://procarelakeland.com")
    print(f"\n✅ Report URL: {url}")
    print(f"📁 Local path: {path}")
