"""
Generate Proper Email Packages with Real PageSpeed Data from JSON files
Creates: PDF audit reports with traffic light tables, HTML emails per email_standards.md
"""
import os
import sys
import json
from datetime import datetime

# Install reportlab if needed
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import inch
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "reportlab"], check=True)
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import inch

# Prospects with verified data
PROSPECTS = [
    {
        "name": "Tony Agnello",
        "business": "Lakeland Air Conditioning",
        "website": "thelakelandac.com",
        "email": "tony@thelakelandac.com",
        "industry": "HVAC",
        "pagespeed_file": "Lakeland_AC_pagespeed.json"
    },
    {
        "name": "Nathane Trimm",
        "business": "Trimm Roofing",
        "website": "trimmroofing.com",
        "email": "support@trimmroofing.com",
        "industry": "Roofing",
        "pagespeed_file": "Trimm_Roofing_pagespeed.json"
    },
    {
        "name": "Chris Shills",
        "business": "Curry Plumbing",
        "website": "curryplumbing.com",
        "email": "chrisshills@curryplumbing.com",
        "industry": "Plumbing",
        "pagespeed_file": "Curry_Plumbing_pagespeed.json"
    },
    {
        "name": "Marshall Andress",
        "business": "Andress Electric",
        "website": "andresselectric.com",
        "email": "info@andresselectric.com",
        "industry": "Electrical",
        "pagespeed_file": "Andress_Electric_pagespeed.json"
    },
    {
        "name": "Bill Lerch",
        "business": "Hunter Plumbing Inc",
        "website": "hunterplumbinginc.com",
        "email": "hunterplumbing@hunterplumbinginc.com",
        "industry": "Plumbing",
        "pagespeed_file": "Hunter_Plumbing_Inc_pagespeed.json"
    },
    {
        "name": "David Smith",
        "business": "Original Pro Plumbing",
        "website": "originalplumber.com",
        "email": "proplumbing1@originalplumber.com",
        "industry": "Plumbing",
        "pagespeed_file": "Original_Pro_Plumbing_pagespeed.json"
    }
]

def load_pagespeed_data(filename):
    """Load real PageSpeed data from JSON file"""
    filepath = os.path.join("pagespeed_results", filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
            mobile = data.get("mobile", {})
            return {
                "success": True,
                "performance_score": mobile.get("score", 0),
                "lcp": mobile.get("lcp", "N/A"),
                "fcp": mobile.get("fcp", "N/A"),
                "cls": mobile.get("cls", "N/A"),
                "speed_index": mobile.get("speed_index", "N/A"),
                "status": "critical" if mobile.get("score", 0) < 50 else "warning" if mobile.get("score", 0) < 90 else "good"
            }
    return {"success": False, "error": "File not found"}


def create_pdf_audit(prospect: dict, pagespeed: dict, output_dir: str) -> str:
    """Create professional 2-4 page PDF audit per email_standards.md with TRAFFIC LIGHT TABLE"""
    
    filename = f"{prospect['business'].replace(' ', '_')}_WebsiteAudit.pdf"
    filepath = os.path.join(output_dir, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom Styles
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
    
    heading2 = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=10
    )
    
    # === PAGE 1: COVER ===
    story.append(Paragraph("Digital Risk &amp; Performance Audit", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>Client:</b> {prospect['business']}", subtitle_style))
    story.append(Paragraph(f"<b>Website:</b> {prospect['website']}", subtitle_style))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("Prepared by:", styles['Normal']))
    story.append(Paragraph("<b>AI Service Co</b>", styles['Heading3']))
    story.append(Paragraph("Daniel Coffman, Owner", styles['Normal']))
    story.append(Paragraph("352-936-8152 | www.aiserviceco.com", styles['Normal']))
    
    story.append(Spacer(1, 60))
    
    # === EXECUTIVE SUMMARY ===
    story.append(Paragraph("EXECUTIVE SUMMARY", heading2))
    story.append(Spacer(1, 10))
    
    if pagespeed.get('success'):
        score = pagespeed['performance_score']
        if score < 50:
            status_text = "CRITICAL PERFORMANCE ISSUES DETECTED"
        elif score < 90:
            status_text = "PERFORMANCE WARNINGS FOUND"
        else:
            status_text = "PERFORMANCE ACCEPTABLE"
            
        summary = f"""Our automated audit of <b>{prospect['website']}</b> has identified several 
        technical issues affecting online visibility and customer acquisition. 
        The website scores <b>{score}/100</b> on Google PageSpeed Insights (Mobile), 
        placing it in the <b>{status_text}</b> category."""
    else:
        summary = f"Our audit identified potential issues with {prospect['website']}."
    
    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # === CRITICAL FINDINGS WITH TRAFFIC LIGHTS ===
    story.append(Paragraph("TRAFFIC LIGHT ASSESSMENT", heading2))
    story.append(Spacer(1, 10))
    
    # Traffic Light symbols
    red_circle = "🔴"
    yellow_circle = "🟡"
    green_circle = "🟢"
    
    if pagespeed.get('success'):
        score = pagespeed['performance_score']
        lcp = pagespeed.get('lcp', 'N/A')
        fcp = pagespeed.get('fcp', 'N/A')
        cls = pagespeed.get('cls', 'N/A')
        
        # Determine status
        if score < 50:
            perf_status = f"{red_circle} CRITICAL"
            perf_detail = f"Mobile PageSpeed: {score}/100 - Losing customers to slow load times"
        elif score < 90:
            perf_status = f"{yellow_circle} WARNING"
            perf_detail = f"Mobile PageSpeed: {score}/100 - Google may penalize rankings"
        else:
            perf_status = f"{green_circle} GOOD"
            perf_detail = f"Mobile PageSpeed: {score}/100 - Meets Google standards"
        
        findings_data = [
            ["AREA", "STATUS", "THE RISK TO THE BUSINESS"],
            ["Mobile Performance", perf_status, perf_detail],
            ["Page Load Speed", f"{yellow_circle} WARNING", f"LCP: {lcp}, FCP: {fcp}"],
            ["Visual Stability", f"{yellow_circle} WARNING" if float(str(cls).replace('\xa0', '')) > 0.1 else f"{green_circle} GOOD", f"CLS: {cls}"],
            ["Privacy Compliance", f"{yellow_circle} WARNING", "Privacy policy status should be verified"],
            ["Lead Capture", f"{green_circle} OPPORTUNITY", "AI intake could optimize lead handling"]
        ]
    else:
        findings_data = [
            ["AREA", "STATUS", "THE RISK TO THE BUSINESS"],
            ["Mobile Performance", f"{red_circle} CRITICAL", "Unable to analyze - site may have issues"],
            ["Privacy Compliance", f"{yellow_circle} WARNING", "Manual verification recommended"],
            ["Lead Capture", f"{green_circle} OPPORTUNITY", "AI intake could optimize lead handling"]
        ]
    
    findings_table = Table(findings_data, colWidths=[1.8*inch, 1.2*inch, 3.5*inch])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    story.append(findings_table)
    story.append(Spacer(1, 30))
    
    # === PROPOSED SOLUTIONS ===
    story.append(Paragraph("PROPOSED SOLUTIONS", heading2))
    story.append(Spacer(1, 10))
    
    solutions = f"""
    <b>1. Performance Optimization (FREE)</b><br/>
    As a local Lakeland business owner, I will fix your mobile performance issues at no cost. 
    This will improve your Google ranking and customer experience.<br/><br/>
    
    <b>2. 14-Day AI Intake Trial</b><br/>
    Install our intelligent intake system that pre-qualifies leads before they reach your team. 
    Your {prospect['industry'].lower()} team will only spend time on high-value opportunities.<br/><br/>
    
    <b>3. Compliance Review</b><br/>
    Ensure your website meets Florida Digital Bill of Rights requirements.
    """
    story.append(Paragraph(solutions, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # === NEXT STEPS ===
    story.append(Paragraph("NEXT STEPS", heading2))
    story.append(Spacer(1, 10))
    
    next_steps = """
    To take advantage of the free performance fix or learn more about our AI intake system, 
    simply reply to this email or call me directly at <b>352-936-8152</b>. 
    I will personally handle your account and ensure results.
    """
    story.append(Paragraph(next_steps, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # === FOOTER ===
    story.append(Paragraph("—" * 40, styles['Normal']))
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
        lcp = pagespeed.get('lcp', 'N/A')
        fcp = pagespeed.get('fcp', 'N/A')
        
        if score < 50:
            perf_status = "🔴 CRITICAL"
            perf_class = "critical"
        elif score < 90:
            perf_status = "🟡 WARNING"
            perf_class = "warning"
        else:
            perf_status = "🟢 GOOD"
            perf_class = "opportunity"
            
        perf_risk = f"Mobile PageSpeed: {score}/100. LCP: {lcp}, FCP: {fcp}"
    else:
        perf_status = "🟡 WARNING"
        perf_class = "warning"
        perf_risk = "Unable to fully analyze - manual review recommended"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6; }}
        .traffic-table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        .traffic-table th {{ background: #1a1a2e; color: white; padding: 12px; text-align: left; }}
        .traffic-table td {{ padding: 10px; border: 1px solid #ddd; }}
        .critical {{ color: #dc3545; font-weight: bold; }}
        .warning {{ color: #856404; font-weight: bold; }}
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
            <td><span class="{perf_class}">{perf_status}</span></td>
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
    trial. We install a digital assistant that pre-screens potential clients before they call - 
    ensuring your team only spends time on high-value opportunities.</p>
    
    <p><strong>MY LOCAL GUARANTEE:</strong> Because I am a local Lakeland resident, I will 
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
    print("GENERATING PROPER EMAIL PACKAGES WITH REAL PAGESPEED DATA")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}")
    print("=" * 70)
    
    output_dir = "email_attachments"
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    for i, prospect in enumerate(PROSPECTS, 1):
        print(f"\n[{i}/{len(PROSPECTS)}] Processing: {prospect['business']}")
        
        # Load real PageSpeed data from JSON
        pagespeed = load_pagespeed_data(prospect['pagespeed_file'])
        if pagespeed['success']:
            print(f"   📊 Score: {pagespeed['performance_score']}/100")
        else:
            print(f"   ⚠️ No PageSpeed data available")
        
        # Create PDF with traffic light table
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
    with open("email_packages_final.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    print(f"✅ Generated {len(results)} email packages with real PageSpeed data")
    print(f"📁 Files saved to: {os.path.abspath(output_dir)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
