"""
Generate Proper Email Packages with PageSpeed Data
Creates: PDF audit reports, PageSpeed data, HTML emails per email_standards.md
"""
import os
import sys
import json
import subprocess
from datetime import datetime

# Check for required packages
try:
    import requests
except ImportError:
    subprocess.run(["pip", "install", "requests"], check=True)
    import requests

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.units import inch
except ImportError:
    subprocess.run(["pip", "install", "reportlab"], check=True)
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.units import inch

# Prospects with verified data
PROSPECTS = [
    {
        "name": "Tony Agnello",
        "business": "Lakeland Air Conditioning",
        "website": "thelakelandac.com",
        "email": "tony@thelakelandac.com",
        "industry": "HVAC"
    },
    {
        "name": "Nathane Trimm",
        "business": "Trimm Roofing",
        "website": "trimmroofing.com",
        "email": "support@trimmroofing.com",
        "industry": "Roofing"
    },
    {
        "name": "Chris Shills",
        "business": "Curry Plumbing",
        "website": "curryplumbing.com",
        "email": "chrisshills@curryplumbing.com",
        "industry": "Plumbing"
    },
    {
        "name": "Marshall Andress",
        "business": "Andress Electric",
        "website": "andresselectric.com",
        "email": "info@andresselectric.com",
        "industry": "Electrical"
    },
    {
        "name": "Bill Lerch",
        "business": "Hunter Plumbing Inc",
        "website": "hunterplumbinginc.com",
        "email": "hunterplumbing@hunterplumbinginc.com",
        "industry": "Plumbing"
    },
    {
        "name": "David Smith",
        "business": "Original Pro Plumbing",
        "website": "originalplumber.com",
        "email": "proplumbing1@originalplumber.com",
        "industry": "Plumbing"
    }
]

# PageSpeed API (free tier, no key needed)
PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

def get_pagespeed_data(website: str) -> dict:
    """Get real PageSpeed Insights data"""
    print(f"   🔍 Analyzing {website}...")
    
    url = f"https://{website}"
    params = {
        "url": url,
        "category": ["PERFORMANCE", "ACCESSIBILITY", "BEST_PRACTICES", "SEO"],
        "strategy": "MOBILE"
    }
    
    try:
        response = requests.get(PAGESPEED_API, params=params, timeout=120)
        if response.status_code == 200:
            data = response.json()
            
            # Extract key metrics
            lighthouse = data.get("lighthouseResult", {})
            categories = lighthouse.get("categories", {})
            audits = lighthouse.get("audits", {})
            
            perf_score = int(categories.get("performance", {}).get("score", 0) * 100)
            seo_score = int(categories.get("seo", {}).get("score", 0) * 100)
            
            # Core Web Vitals
            lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
            fcp = audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
            cls = audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")
            tbt = audits.get("total-blocking-time", {}).get("displayValue", "N/A")
            
            return {
                "success": True,
                "performance_score": perf_score,
                "seo_score": seo_score,
                "lcp": lcp,
                "fcp": fcp,
                "cls": cls,
                "tbt": tbt,
                "status": "critical" if perf_score < 50 else "warning" if perf_score < 90 else "good"
            }
        else:
            print(f"   ⚠️ API returned {response.status_code}")
            return {"success": False, "error": f"API error: {response.status_code}"}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def create_pdf_audit(prospect: dict, pagespeed: dict, output_dir: str) -> str:
    """Create professional 2-4 page PDF audit per email_standards.md"""
    
    filename = f"{prospect['business'].replace(' ', '_')}_WebsiteAudit.pdf"
    filepath = os.path.join(output_dir, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title Style
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1a1a2e')
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=20,
        textColor=colors.HexColor('#4a4a4a')
    )
    
    # === PAGE 1: COVER ===
    story.append(Paragraph("Digital Risk & Performance Audit", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>Client:</b> {prospect['business']}", subtitle_style))
    story.append(Paragraph(f"<b>Website:</b> {prospect['website']}", subtitle_style))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Prepared by:", styles['Normal']))
    story.append(Paragraph("<b>AI Service Co</b>", styles['Heading3']))
    story.append(Paragraph("Daniel Coffman, Owner", styles['Normal']))
    story.append(Paragraph("352-936-8152 | www.aiserviceco.com", styles['Normal']))
    
    story.append(Spacer(1, 100))
    
    # === EXECUTIVE SUMMARY ===
    story.append(Paragraph("EXECUTIVE SUMMARY", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    if pagespeed.get('success'):
        score = pagespeed['performance_score']
        if score < 50:
            status_text = "CRITICAL PERFORMANCE ISSUES DETECTED"
            color = colors.red
        elif score < 90:
            status_text = "PERFORMANCE WARNINGS FOUND"
            color = colors.orange
        else:
            status_text = "PERFORMANCE ACCEPTABLE"
            color = colors.green
            
        summary = f"""Our automated audit of {prospect['website']} has identified several 
        technical issues that may be affecting your online visibility and customer acquisition. 
        The website currently scores <b>{score}/100</b> on Google's PageSpeed Insights, 
        which places it in the <font color="{color.hexval()}">{status_text}</font> category."""
    else:
        summary = f"Our audit identified potential issues with {prospect['website']}."
    
    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # === CRITICAL FINDINGS WITH TRAFFIC LIGHTS ===
    story.append(Paragraph("CRITICAL FINDINGS", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # Traffic Light Table
    if pagespeed.get('success'):
        score = pagespeed['performance_score']
        
        # Determine status colors
        perf_color = colors.red if score < 50 else colors.orange if score < 90 else colors.green
        perf_status = "🔴 CRITICAL" if score < 50 else "🟡 WARNING" if score < 90 else "🟢 GOOD"
        
        findings_data = [
            ["Area", "Status", "Impact"],
            ["Mobile Performance", perf_status, f"Score: {score}/100. LCP: {pagespeed.get('lcp', 'N/A')}"],
            ["Page Load Speed", "🟡 WARNING", f"FCP: {pagespeed.get('fcp', 'N/A')}, TBT: {pagespeed.get('tbt', 'N/A')}"],
            ["Privacy Compliance", "🟡 WARNING", "Privacy policy status should be verified"],
            ["Lead Capture", "🟢 OPPORTUNITY", "AI intake could optimize lead handling"]
        ]
    else:
        findings_data = [
            ["Area", "Status", "Impact"],
            ["Mobile Performance", "🔴 CRITICAL", "Unable to analyze - site may be down"],
            ["Privacy Compliance", "🟡 WARNING", "Manual verification recommended"],
            ["Lead Capture", "🟢 OPPORTUNITY", "AI intake could optimize lead handling"]
        ]
    
    findings_table = Table(findings_data, colWidths=[2*inch, 1.5*inch, 3*inch])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(findings_table)
    story.append(Spacer(1, 30))
    
    # === PROPOSED SOLUTIONS ===
    story.append(Paragraph("PROPOSED SOLUTIONS", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    solutions = f"""
    <b>1. Performance Optimization (FREE)</b><br/>
    As a local Lakeland business owner, I would like to fix your mobile performance issues at no cost. 
    This will improve your Google ranking and customer experience.<br/><br/>
    
    <b>2. 14-Day AI Intake Trial</b><br/>
    Install our intelligent intake system that pre-qualifies leads before they reach your team. 
    Your {prospect['industry'].lower()} team will only spend time on high-value opportunities.<br/><br/>
    
    <b>3. Compliance Review</b><br/>
    Ensure your website meets Florida Digital Bill of Rights requirements for customer data collection.
    """
    story.append(Paragraph(solutions, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # === NEXT STEPS ===
    story.append(Paragraph("NEXT STEPS", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    next_steps = """
    To take advantage of the free performance fix or learn more about our AI intake system, 
    simply reply to this email or call me directly at <b>352-936-8152</b>. 
    I will personally handle your account and ensure results.
    """
    story.append(Paragraph(next_steps, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # === FOOTER ===
    story.append(Paragraph("—" * 30, styles['Normal']))
    story.append(Paragraph("<b>AI Service Co</b> | Lakeland, FL", styles['Normal']))
    story.append(Paragraph("www.aiserviceco.com | 352-936-8152", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"   ✅ Created: {filename}")
    
    return filepath


def create_html_email(prospect: dict, pagespeed: dict) -> str:
    """Create HTML email with traffic light table per email_standards.md"""
    
    if pagespeed.get('success'):
        score = pagespeed['performance_score']
        perf_status = "🔴 CRITICAL" if score < 50 else "🟡 WARNING" if score < 90 else "🟢 GOOD"
        perf_risk = f"Mobile PageSpeed: {score}/100. LCP: {pagespeed.get('lcp', 'N/A')}"
    else:
        perf_status = "🟡 WARNING"
        perf_risk = "Unable to fully analyze - manual review recommended"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 14px; color: #333; }}
        .traffic-table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        .traffic-table th {{ background: #1a1a2e; color: white; padding: 12px; text-align: left; }}
        .traffic-table td {{ padding: 10px; border: 1px solid #ddd; }}
        .critical {{ color: #dc3545; font-weight: bold; }}
        .warning {{ color: #ffc107; font-weight: bold; }}
        .opportunity {{ color: #28a745; font-weight: bold; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #666; border-top: 1px solid #ddd; padding-top: 15px; }}
    </style>
</head>
<body>
    <p>Dear {prospect['name']},</p>
    
    <p>I am a local digital strategist here in Lakeland, and I've conducted a brief health audit of 
    {prospect['business']}'s online presence.</p>
    
    <p>To save you time, I have summarized the three critical areas that currently impact your 
    online reputation, search ranking, and lead flow:</p>
    
    <table class="traffic-table">
        <tr>
            <th>AREA</th>
            <th>STATUS</th>
            <th>THE RISK TO THE BUSINESS</th>
        </tr>
        <tr>
            <td>Mobile Performance</td>
            <td><span class="critical">{perf_status}</span></td>
            <td>{perf_risk}</td>
        </tr>
        <tr>
            <td>Privacy Compliance</td>
            <td><span class="warning">🟡 WARNING</span></td>
            <td>Under the Florida Digital Bill of Rights, a visible Privacy Policy is required.</td>
        </tr>
        <tr>
            <td>Lead Efficiency</td>
            <td><span class="opportunity">🟢 OPPORTUNITY</span></td>
            <td>AI-powered intake could pre-qualify leads before they reach your team.</td>
        </tr>
    </table>
    
    <p><strong>THE SOLUTION:</strong> I specialize in helping {prospect['industry'].lower()} businesses 
    bridge these technical gaps. I would like to offer {prospect['business']} a 14-day "Intelligent Intake" 
    trial. We can install a digital assistant that pre-screens potential clients before they call - 
    ensuring your team only spends time on high-value cases.</p>
    
    <p><strong>MY LOCAL GUARANTEE:</strong> Because I am a local Lakeland resident, I would like to 
    fix your Mobile Performance issue for free this week. This will move your site back into the 
    "Green" zone and allow you to see the quality of my work firsthand with zero risk.</p>
    
    <p><strong>I have attached your full Performance Report.</strong> I will follow up with your 
    office in an hour to see if you have any questions.</p>
    
    <p>Best regards,</p>
    
    <p>
        <strong>Daniel Coffman</strong><br/>
        Owner, AI Service Co<br/>
        352-936-8152<br/>
        www.aiserviceco.com
    </p>
    
    <div class="footer">
        <p>AI Service Co | Lakeland, FL 33801</p>
        <p>If you'd prefer not to receive emails about website performance, 
        reply with "REMOVE" and I'll update my list immediately.</p>
    </div>
</body>
</html>"""
    
    return html


def main():
    print("=" * 70)
    print("GENERATING PROPER EMAIL PACKAGES PER EMAIL_STANDARDS.MD")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}")
    print("=" * 70)
    
    output_dir = "email_attachments"
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    for i, prospect in enumerate(PROSPECTS, 1):
        print(f"\n[{i}/{len(PROSPECTS)}] Processing: {prospect['business']}")
        
        # Get PageSpeed data
        pagespeed = get_pagespeed_data(prospect['website'])
        
        # Create PDF
        pdf_path = create_pdf_audit(prospect, pagespeed, output_dir)
        
        # Create HTML email
        html = create_html_email(prospect, pagespeed)
        html_path = os.path.join(output_dir, f"{prospect['business'].replace(' ', '_')}_Email.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   ✅ Created: {os.path.basename(html_path)}")
        
        # Save data
        results.append({
            "prospect": prospect,
            "pagespeed": pagespeed,
            "pdf": pdf_path,
            "html": html_path
        })
    
    # Save results
    with open("email_packages.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    print(f"✅ Generated {len(results)} email packages")
    print(f"📁 Files saved to: {os.path.abspath(output_dir)}")
    print("\nNext: Run send_proper_previews.py to send to Dan for approval")
    print("=" * 70)


if __name__ == "__main__":
    main()
