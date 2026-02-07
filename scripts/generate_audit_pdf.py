"""
Generate Professional PDF Audit Reports with Colored Traffic Light Tables
Uses ReportLab per AI Visibility Audit Standards KI
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
from datetime import datetime

# Color palette from KI
COLORS = {
    'red': colors.HexColor('#dc3545'),
    'light_red': colors.HexColor('#f8d7da'),
    'yellow': colors.HexColor('#856404'),
    'light_yellow': colors.HexColor('#fff3cd'),
    'green': colors.HexColor('#155724'),
    'light_green': colors.HexColor('#d4edda'),
    'header_bg': colors.HexColor('#1a1a2e'),
    'white': colors.white,
    'grey': colors.HexColor('#6c757d')
}

def generate_audit_pdf(prospect, output_path):
    """Generate a professional PDF audit report with colored tables"""
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=COLORS['header_bg'],
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=COLORS['grey'],
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=COLORS['header_bg'],
        spaceBefore=20,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=11,
        leading=16
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph(f"Website Audit Report", title_style))
    elements.append(Paragraph(f"{prospect['business']}", subtitle_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", 
                              ParagraphStyle('Date', fontSize=10, textColor=COLORS['grey'], alignment=TA_CENTER)))
    elements.append(Spacer(1, 30))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", section_style))
    elements.append(Paragraph(
        f"This audit identified compliance risks and performance issues on {prospect['url']}. "
        f"Critical findings require immediate attention to avoid potential legal liability.",
        body_style
    ))
    elements.append(Spacer(1, 20))
    
    # Traffic Light Table
    elements.append(Paragraph("Audit Findings", section_style))
    
    table_data = [
        ['Area', 'Status', 'Finding']
    ]
    
    # Add rows
    table_data.append(['Legal Compliance', 'CRITICAL', prospect['liability_issues'][0]])
    table_data.append(['Mobile Speed', 'WARNING' if prospect['speed_score'] >= 50 else 'CRITICAL', 
                       f"PageSpeed Score: {prospect['speed_score']}/100"])
    table_data.append(['Lead Capture', 'OPPORTUNITY', prospect['growth_opps'][0]])
    
    table = Table(table_data, colWidths=[1.5*inch, 1.0*inch, 4.0*inch])
    
    table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), COLORS['header_bg']),
        ('TEXTCOLOR', (0, 0), (-1, 0), COLORS['white']),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        
        # Critical row (Legal)
        ('BACKGROUND', (0, 1), (-1, 1), COLORS['light_red']),
        ('TEXTCOLOR', (1, 1), (1, 1), COLORS['red']),
        ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
        
        # Warning row (Speed)
        ('BACKGROUND', (0, 2), (-1, 2), COLORS['light_yellow']),
        ('TEXTCOLOR', (1, 2), (1, 2), COLORS['yellow']),
        ('FONTNAME', (1, 2), (1, 2), 'Helvetica-Bold'),
        
        # Opportunity row (Lead Capture)
        ('BACKGROUND', (0, 3), (-1, 3), COLORS['light_green']),
        ('TEXTCOLOR', (1, 3), (1, 3), COLORS['green']),
        ('FONTNAME', (1, 3), (1, 3), 'Helvetica-Bold'),
        
        # Grid and alignment
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 25))
    
    # Critical Finding Detail
    elements.append(Paragraph("🔴 Critical Finding: Legal Compliance", section_style))
    
    for issue in prospect['liability_issues']:
        elements.append(Paragraph(f"• {issue}", body_style))
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "<b>Risk:</b> TCPA violations carry fines of $500-$1,500 per incident. "
        "Recent case: Optum RX settled for $23.5M in class action over consent violations.",
        body_style
    ))
    elements.append(Spacer(1, 20))
    
    # Performance Issues
    elements.append(Paragraph("🟡 Performance Issues", section_style))
    
    for issue in prospect['performance_issues']:
        elements.append(Paragraph(f"• {issue}", body_style))
    elements.append(Spacer(1, 20))
    
    # Growth Opportunities
    elements.append(Paragraph("🟢 Growth Opportunities", section_style))
    
    for opp in prospect['growth_opps']:
        elements.append(Paragraph(f"• {opp}", body_style))
    elements.append(Spacer(1, 25))
    
    # Available Services
    elements.append(Paragraph("Available Services", section_style))
    
    services = [
        "🤖 AI Receptionist – 24/7 call answering & appointment booking",
        "📧 Newsletter Automation – Customer nurturing campaigns",
        "📱 Smart Social Reply – Facebook/Instagram AI response",
        "🎯 Visionary Ads – AI-powered ad creative",
        "⭐ Review Management – Automated review requests",
        "⚖️ Compliance Package – Terms/Privacy/TCPA compliance"
    ]
    
    for svc in services:
        elements.append(Paragraph(f"• {svc}", body_style))
    
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Contact us for custom pricing based on your needs.", 
                              ParagraphStyle('Note', fontSize=10, textColor=COLORS['grey'])))
    elements.append(Spacer(1, 25))
    
    # Free Offer
    elements.append(Paragraph("✅ Free Offer (No Strings Attached)", section_style))
    elements.append(Paragraph("1. <b>Free TCPA/Compliance Fix</b> – We'll add proper consent checkboxes and Terms/Privacy pages at zero cost.", body_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("2. <b>14-Day AI Receptionist Trial</b> – Test our 24/7 call answering system with no commitment.", body_style))
    elements.append(Spacer(1, 30))
    
    # Contact
    elements.append(Paragraph(
        "<b>Daniel Coffman</b> | 352-936-8152 | AI Service Co<br/>www.aiserviceco.com | Lakeland, FL",
        ParagraphStyle('Contact', fontSize=11, alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(elements)
    return output_path

if __name__ == "__main__":
    # Test
    test_prospect = {
        "business": "Test Business",
        "url": "https://example.com",
        "liability_issues": ["Missing TCPA consent checkbox", "No privacy policy link"],
        "performance_issues": ["PageSpeed 65 – slow load", "No mobile optimization"],
        "growth_opps": ["24/7 AI Receptionist", "Review automation"],
        "speed_score": 65
    }
    
    output = generate_audit_pdf(test_prospect, "test_audit.pdf")
    print(f"Generated: {output}")
