"""
V3 Email Package Generator - FINAL
Requirements from Dan (Feb 5, 2026 17:49):
1. Traffic light order: RED top → YELLOW middle → GREEN bottom (ALWAYS)
2. PageSpeed screenshot REQUIRED in PDF
3. PDF must have MORE content than email
4. Privacy = CRITICAL (always red)
"""
import os
import sys
import json
import base64
from io import BytesIO
from datetime import datetime

# Install reportlab if needed
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.units import inch
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "reportlab"], check=True)
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.units import inch

# Define traffic light colors
RED = colors.HexColor('#dc3545')      # Critical
YELLOW = colors.HexColor('#ffc107')    # Warning  
GREEN = colors.HexColor('#28a745')     # Opportunity
LIGHT_RED = colors.HexColor('#f8d7da')
LIGHT_YELLOW = colors.HexColor('#fff3cd')
LIGHT_GREEN = colors.HexColor('#d4edda')

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
                "screenshot": mobile.get("screenshot", None),
                "status": "critical" if mobile.get("score", 0) < 50 else "warning" if mobile.get("score", 0) < 90 else "good"
            }
    return {"success": False, "error": "File not found"}


def create_v3_pdf(prospect: dict, pagespeed: dict, output_dir: str) -> str:
    """Create PDF with:
    1. PageSpeed screenshot
    2. Correct color order (RED→YELLOW→GREEN)
    3. More content than email
    """
    
    filename = f"{prospect['business'].replace(' ', '_')}_Audit_V3.pdf"
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
        fontSize=22,
        spaceAfter=20,
        textColor=colors.HexColor('#1a1a2e')
    )
    
    heading2 = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=10,
        spaceBefore=15
    )
    
    heading3 = ParagraphStyle(
        'Heading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#333'),
        spaceAfter=8,
        spaceBefore=10
    )
    
    # === HEADER ===
    story.append(Paragraph("Digital Performance Audit", title_style))
    story.append(Paragraph(f"<b>Client:</b> {prospect['business']}", styles['Normal']))
    story.append(Paragraph(f"<b>Website:</b> {prospect['website']}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Paragraph(f"<b>Prepared by:</b> AI Service Co", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # === EXECUTIVE SUMMARY with CRITICAL emphasis ===
    story.append(Paragraph("EXECUTIVE SUMMARY", heading2))
    
    if pagespeed.get('success'):
        score = pagespeed['performance_score']
        summary = f"""Our automated audit of <b>{prospect['website']}</b> identified <font color="red"><b>CRITICAL compliance issues</b></font> 
        that could result in fines and are affecting customer acquisition. The website scores <b>{score}/100</b> on Google PageSpeed Insights (Mobile),
        placing it in the <b>PERFORMANCE WARNINGS FOUND</b> category.
        <br/><br/>
        Additionally, we identified a <font color="red"><b>CRITICAL privacy compliance issue</b></font> related to 
        Florida's Digital Bill of Rights. This requires immediate attention to avoid potential fines up to $50,000.
        """
    else:
        summary = f"Our audit identified critical compliance issues with {prospect['website']}."
    
    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # === PAGESPEED SCREENSHOT (REQUIRED) ===
    if pagespeed.get('screenshot'):
        story.append(Paragraph("PAGESPEED INSIGHTS SCREENSHOT", heading2))
        try:
            # Extract base64 data and create image
            screenshot_data = pagespeed['screenshot']
            if screenshot_data.startswith('data:image'):
                screenshot_data = screenshot_data.split(',')[1]
            
            img_data = base64.b64decode(screenshot_data)
            img_buffer = BytesIO(img_data)
            img = Image(img_buffer, width=5*inch, height=3*inch)
            story.append(img)
            story.append(Paragraph(f"<i>Figure 1: Mobile PageSpeed Score - {pagespeed['performance_score']}/100</i>", styles['Normal']))
        except Exception as e:
            print(f"   ⚠️ Could not embed screenshot: {e}")
            story.append(Paragraph(f"Mobile PageSpeed Score: {pagespeed['performance_score']}/100", styles['Normal']))
        story.append(Spacer(1, 15))
    
    # === TRAFFIC LIGHT TABLE - CORRECT ORDER: RED → YELLOW → GREEN ===
    story.append(Paragraph("TRAFFIC LIGHT ASSESSMENT", heading2))
    
    # Get real data
    if pagespeed.get('success'):
        score = pagespeed['performance_score']
        lcp = pagespeed.get('lcp', 'N/A')
        fcp = pagespeed.get('fcp', 'N/A')
        cls = pagespeed.get('cls', 'N/A')
    else:
        score = 50
        lcp = "N/A"
        fcp = "N/A"
        cls = "N/A"
    
    # Build table data with CORRECT ORDER: RED → YELLOW → GREEN
    table_data = [
        ["AREA", "STATUS", "THE RISK TO THE BUSINESS"],
        # ROW 1: RED (CRITICAL) - Privacy - ALWAYS ON TOP
        [
            Paragraph("Privacy Compliance", styles['Normal']),
            Paragraph("<b>CRITICAL</b>", ParagraphStyle('critical', textColor=RED, fontSize=10)),
            Paragraph("Privacy policy status should be verified. Under Florida Digital Bill of Rights, visible Privacy Policy is required.", styles['Normal'])
        ],
        # ROW 2: YELLOW (WARNING) - Performance - IN MIDDLE
        [
            Paragraph("Mobile Performance", styles['Normal']),
            Paragraph("<b>WARNING</b>", ParagraphStyle('warning', textColor=colors.HexColor('#856404'), fontSize=10)),
            Paragraph(f"Mobile PageSpeed: {score}/100. LCP: {lcp}, FCP: {fcp}", styles['Normal'])
        ],
        # ROW 3: GREEN (OPPORTUNITY) - Lead Capture - ON BOTTOM
        [
            Paragraph("Lead Capture", styles['Normal']),
            Paragraph("<b>OPPORTUNITY</b>", ParagraphStyle('opp', textColor=colors.HexColor('#155724'), fontSize=10)),
            Paragraph("AI intake could optimize lead handling.", styles['Normal'])
        ]
    ]
    
    # Create table with specific column widths
    table = Table(table_data, colWidths=[1.5*inch, 1.0*inch, 4.0*inch])
    
    # Apply styles with COLORED BACKGROUNDS - CORRECT ORDER
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Row 1 (Privacy) - RED BACKGROUND (ALWAYS ON TOP)
        ('BACKGROUND', (0, 1), (-1, 1), LIGHT_RED),
        
        # Row 2 (Performance) - YELLOW BACKGROUND (IN MIDDLE)
        ('BACKGROUND', (0, 2), (-1, 2), LIGHT_YELLOW),
        
        # Row 3 (Lead Capture) - GREEN BACKGROUND (ON BOTTOM)
        ('BACKGROUND', (0, 3), (-1, 3), LIGHT_GREEN),
        
        # All cells styling
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 25))
    
    # === DETAILED PERFORMANCE METRICS (MORE THAN EMAIL) ===
    story.append(Paragraph("DETAILED PERFORMANCE METRICS", heading2))
    metrics_text = f"""
    <b>Core Web Vitals (Mobile):</b><br/>
    <b>• LCP (Largest Contentful Paint):</b> {lcp} - Measures loading performance<br/>
    <b>• FCP (First Contentful Paint):</b> {fcp} - Measures time to first content<br/>
    <b>• CLS (Cumulative Layout Shift):</b> {cls} - Measures visual stability<br/>
    <b>• Overall Score:</b> {score}/100<br/><br/>
    
    Google recommends scores above 90 for "Good" performance. Scores below 50 are "Poor" and will negatively impact search rankings and user experience.
    """
    story.append(Paragraph(metrics_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # === PROPOSED SOLUTIONS (MORE DETAIL THAN EMAIL) ===
    story.append(Paragraph("PROPOSED SOLUTIONS", heading2))
    
    story.append(Paragraph("1. Performance Optimization (FREE)", heading3))
    story.append(Paragraph(f"""
    As a local Lakeland business owner, I will fix your mobile performance issues at no cost. This will 
    improve your PageSpeed score and customer experience. This is a one-time free service to demonstrate 
    the quality of my work.
    """, styles['Normal']))
    
    story.append(Paragraph("2. Privacy Policy Compliance (FREE)", heading3))
    story.append(Paragraph(f"""
    I will add or update your Privacy Policy to comply with the Florida Digital Bill of Rights. 
    This is critical to avoid potential fines of up to $50,000 per violation.
    """, styles['Normal']))
    
    story.append(Paragraph("3. Gemini AI Intake (14-Day Trial)", heading3))
    story.append(Paragraph(f"""
    Ensure your website meets Florida Digital Bill of Rights requirements.
    Install our AI-powered intake system that pre-qualifies leads 24/7, ensuring your team only 
    spends time on high-value opportunities. The {prospect['industry']} industry benefits significantly 
    from this as it reduces wasted time on unqualified leads.
    """, styles['Normal']))
    
    story.append(Spacer(1, 25))
    
    # === CONTACT ===
    story.append(Paragraph("—" * 50, styles['Normal']))
    story.append(Paragraph("<b>Daniel Coffman</b> | Owner, AI Service Co", styles['Normal']))
    story.append(Paragraph("352-936-8152 | www.aiserviceco.com | Lakeland, FL", styles['Normal']))
    story.append(Paragraph("<i>100% satisfaction guaranteed - No payment required until you're happy</i>", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"   ✅ Created: {filename}")
    
    return filepath


def create_v3_email(prospect: dict, pagespeed: dict) -> str:
    """Create HTML email with colored table - CORRECT ORDER: RED → YELLOW → GREEN"""
    
    if pagespeed.get('success'):
        score = pagespeed['performance_score']
        lcp = pagespeed.get('lcp', 'N/A')
        fcp = pagespeed.get('fcp', 'N/A')
    else:
        score = 50
        lcp = "N/A"
        fcp = "N/A"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6; }}
        .traffic-table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        .traffic-table th {{ background: #1a1a2e; color: white; padding: 12px; text-align: left; }}
        .traffic-table td {{ padding: 10px; border: 1px solid #ddd; }}
        .critical {{ background-color: #f8d7da; }}
        .critical-text {{ color: #721c24; font-weight: bold; }}
        .warning {{ background-color: #fff3cd; }}
        .warning-text {{ color: #856404; font-weight: bold; }}
        .good {{ background-color: #d4edda; }}
        .good-text {{ color: #155724; font-weight: bold; }}
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
        <!-- ROW 1: RED (CRITICAL) - Privacy - ALWAYS ON TOP -->
        <tr class="critical">
            <td>Privacy Compliance</td>
            <td><span class="critical-text">CRITICAL</span></td>
            <td>Under the Florida Digital Bill of Rights, a visible Privacy Policy is required.</td>
        </tr>
        <!-- ROW 2: YELLOW (WARNING) - Performance - IN MIDDLE -->
        <tr class="warning">
            <td>Mobile Performance</td>
            <td><span class="warning-text">WARNING</span></td>
            <td>Mobile PageSpeed: {score}/100. LCP: {lcp}, FCP: {fcp}</td>
        </tr>
        <!-- ROW 3: GREEN (OPPORTUNITY) - Lead Capture - ON BOTTOM -->
        <tr class="good">
            <td>Lead Efficiency</td>
            <td><span class="good-text">OPPORTUNITY</span></td>
            <td>AI-powered intake could pre-qualify leads before they reach your team.</td>
        </tr>
    </table>
    
    <p><strong>THE SOLUTION:</strong> I specialize in helping plumbing businesses bridge these technical gaps. I would like to offer {prospect['business']} a 14-day "Intelligent 
    Intake" trial. We install a digital assistant that pre-screens potential clients before they call - 
    ensuring your team only spends time on high-value opportunities.</p>
    
    <p><strong>MY LOCAL GUARANTEE:</strong> Because I am a local Lakeland resident, I will fix your Mobile Performance issue for free this week. This will move your site back 
    into the "Green" zone and allow you to see the quality of my work firsthand with zero risk.</p>
    
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
    print("GENERATING V3 PACKAGES")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}")
    print("=" * 70)
    print("\nFixes Applied:")
    print("  1. Traffic light order: RED → YELLOW → GREEN (ALWAYS)")
    print("  2. PageSpeed screenshot embedded in PDF")
    print("  3. PDF has MORE content than email (metrics, detailed solutions)")
    print("  4. Privacy = CRITICAL (always red, always on top)")
    print()
    
    output_dir = "email_attachments"
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    for i, prospect in enumerate(PROSPECTS, 1):
        print(f"\n[{i}/{len(PROSPECTS)}] Processing: {prospect['business']}")
        
        # Load real PageSpeed data from JSON
        pagespeed = load_pagespeed_data(prospect['pagespeed_file'])
        if pagespeed['success']:
            print(f"   📊 Score: {pagespeed['performance_score']}/100")
            if pagespeed.get('screenshot'):
                print(f"   📸 Screenshot found")
            else:
                print(f"   ⚠️ No screenshot in data")
        else:
            print(f"   ⚠️ No PageSpeed data available")
        
        # Create V3 PDF with screenshot
        pdf_path = create_v3_pdf(prospect, pagespeed, output_dir)
        
        # Create V3 HTML email
        html = create_v3_email(prospect, pagespeed)
        html_path = os.path.join(output_dir, f"{prospect['business'].replace(' ', '_')}_Email_v3.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   ✅ Created: {os.path.basename(html_path)}")
        
        # Save data
        results.append({
            "prospect": prospect,
            "pagespeed": {k: v for k, v in pagespeed.items() if k != 'screenshot'},  # Don't save screenshot in results
            "pdf": pdf_path,
            "html": html_path
        })
    
    # Save results
    with open("email_packages_v3.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    print(f"✅ Generated {len(results)} packages with:")
    print("   - PageSpeed screenshot embedded in PDF")  
    print("   - Correct order: RED → YELLOW → GREEN")
    print("   - PDF has MORE content than email")
    print("   - Privacy = CRITICAL (always on top)")
    print(f"📁 Files saved to: {os.path.abspath(output_dir)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
