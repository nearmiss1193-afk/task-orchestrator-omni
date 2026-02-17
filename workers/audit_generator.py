"""
AI Visibility Audit Generator — Traffic Light Protocol
=======================================================
Board Consensus: Feb 9, 2026

Generates personalized AI visibility audit PDFs for leads.
Uses Google PageSpeed Insights API (free) + privacy policy check.
Outputs ReportLab PDF with Traffic Light table (Red/Yellow/Green).

FDBR Compliance Hook: Every lead without a privacy policy = CRITICAL (Red).
This is the emotional trigger that gets replies.

Sovereign Law: "The audit sells the service. The email delivers the audit."
"""

import os
import io
import base64
import requests
import traceback
from urllib.parse import urlparse
from google import genai # 2026 GenAI SDK


# ──────────────────────────────────────────────────────────
#  PAGESPEED INSIGHTS (Free, no key required for basic use)
# ──────────────────────────────────────────────────────────

def fetch_pagespeed(website_url: str) -> dict:
    """
    Fetches PageSpeed Insights for a URL (mobile strategy).
    Returns dict with score, metrics, and status.
    Falls back to defaults if API fails.
    """
    result = {
        "score": None,
        "fcp": None,           # First Contentful Paint
        "lcp": None,           # Largest Contentful Paint
        "cls": None,           # Cumulative Layout Shift
        "speed_index": None,
        "status": "unknown",   # good / warning / critical
        "raw_score": None,
    }

    # Normalize URL
    if not website_url.startswith("http"):
        website_url = f"https://{website_url}"

    # Use API key rotation to avoid 429 rate limits
    import random
    api_keys = [
        os.environ.get("GOOGLE_PLACES_API_KEY"),
        os.environ.get("GOOGLE_API_KEY"),
        "AIzaSyCtDhszpASBGBrW7A7tuX3N8txDflx_i4o", # Empire-Email-Integration
        "AIzaSyDVL4vfogtIKRLqOFNPMcKOg1LEAb9dipc", # Fallback Key
        "AIzaSyALaxJstr7hiyyC52zTZOd2ymow5v1-PKY"  # Secondary Fallback
    ]
    api_keys = [k for k in api_keys if k and k != "AIzaSyALaxJstr7hiyyC52zTZOd2ymow5v1-PKY" or k] # Clean list
    
    # Shuffle or rotate
    random.shuffle(api_keys)
    
    last_error = None
    for api_key in api_keys:
        api_url = (
            f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            f"?url={website_url}&strategy=mobile&category=performance&key={api_key}"
        )
        try:
            r = requests.get(api_url, timeout=45)
            if r.status_code == 200:
                data = r.json()
                lighthouse = data.get("lighthouseResult", {})
                categories = lighthouse.get("categories", {})
                perf = categories.get("performance", {})
                score = perf.get("score")  # 0.0 to 1.0

                if score is not None:
                    result["raw_score"] = score
                    result["score"] = int(score * 100)

                    if result["score"] >= 90:
                        result["status"] = "good"
                    elif result["score"] >= 50:
                        result["status"] = "warning"
                    else:
                        result["status"] = "critical"

                # Extract key metrics
                audits = lighthouse.get("audits", {})
                result["fcp"] = audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
                result["lcp"] = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
                result["cls"] = audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")
                result["speed_index"] = audits.get("speed-index", {}).get("displayValue", "N/A")

                print(f"  ✅ PageSpeed Success ({api_key[:8]}...): {result['score']}/100")
                return result
            elif r.status_code == 429:
                print(f"  ⚠️ Key {api_key[:8]}... rate limited (429), rotating...")
                continue
            else:
                print(f"  ❌ PageSpeed API {r.status_code} for key {api_key[:8]}...")
                last_error = f"HTTP {r.status_code}"
                continue
        except Exception as e:
            print(f"  ❌ PageSpeed Connection Error for {api_key[:8]}...: {e}")
            last_error = str(e)
            continue

    return result


# ──────────────────────────────────────────────────────────
#  PRIVACY POLICY CHECK (FDBR Compliance)
# ──────────────────────────────────────────────────────────

def check_privacy_policy(website_url: str) -> dict:
    """
    Checks if a website has a visible privacy policy page.
    FDBR requires Florida businesses to have a compliant policy.
    
    Returns dict with found (bool), url, and status (always critical if missing).
    """
    result = {
        "found": False,
        "url": None,
        "status": "critical",  # Default: CRITICAL (the hook)
        "details": "No privacy policy found — potential FDBR violation"
    }

    if not website_url.startswith("http"):
        website_url = f"https://{website_url}"

    # Common privacy policy paths
    paths = ["/privacy", "/privacy-policy", "/privacypolicy", "/legal/privacy"]

    for path in paths:
        try:
            check_url = f"{website_url.rstrip('/')}{path}"
            r = requests.get(check_url, timeout=10, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 500:
                # Check if it actually mentions privacy
                text_lower = r.text.lower()
                if any(kw in text_lower for kw in ["privacy", "personal data", "information we collect", "cookies"]):
                    result["found"] = True
                    result["url"] = check_url
                    result["status"] = "warning"  # Found but probably not FDBR-compliant
                    result["details"] = "Privacy policy found but may not be FDBR-compliant (missing required disclosures)"
                    print(f"  Privacy policy found at {path} (warning: compliance uncertain)")
                    return result
        except Exception:
            continue

    # Also check the homepage for a privacy link
    try:
        r = requests.get(website_url, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            text_lower = r.text.lower()
            if "privacy policy" in text_lower or "privacy-policy" in text_lower:
                result["found"] = True
                result["status"] = "warning"
                result["details"] = "Privacy policy link found on homepage but page not verified"
                print(f"  Privacy policy link found on homepage")
                return result
    except Exception:
        pass

    print(f"  Privacy policy: NOT FOUND (CRITICAL)")
    return result


# ──────────────────────────────────────────────────────────
#  AI READINESS CHECK
# ──────────────────────────────────────────────────────────

def check_ai_readiness(website_url: str) -> dict:
    """
    Quick check: does the site have chat widgets, booking forms, or AI features?
    """
    result = {
        "has_chat": False,
        "has_booking": False,
        "has_schema": False,
        "status": "warning",  # Default: room for improvement
        "details": "No AI-powered features detected"
    }

    if not website_url.startswith("http"):
        website_url = f"https://{website_url}"

    try:
        r = requests.get(website_url, timeout=10, allow_redirects=True)
        if r.status_code != 200:
            return result

        text = r.text.lower()

        # Chat widgets
        chat_indicators = ["tidio", "intercom", "drift", "livechat", "tawk", "zendesk", "crisp", "chat-widget"]
        result["has_chat"] = any(ci in text for ci in chat_indicators)

        # Booking / scheduling
        booking_indicators = ["calendly", "acuity", "booking", "schedule", "appointment", "housecallpro", "servicetitan"]
        result["has_booking"] = any(bi in text for bi in booking_indicators)

        # Schema markup
        result["has_schema"] = '"@type"' in text or "'@type'" in text

        if result["has_chat"] and result["has_booking"] and result["has_schema"]:
            result["status"] = "good"
            result["details"] = "Site has chat, booking, and structured data"
        elif result["has_chat"] or result["has_booking"]:
            result["status"] = "warning"
            features = []
            if result["has_chat"]:
                features.append("chat")
            if result["has_booking"]:
                features.append("booking")
            result["details"] = f"Has {', '.join(features)} but missing other AI features"
        else:
            result["status"] = "critical"
            result["details"] = "No chat widget, booking system, or structured data found"

    except Exception as e:
        print(f"  AI readiness check error: {e}")

    return result


# ──────────────────────────────────────────────────────────
#  VEO 3.1 VIDEO TEASER (Cinematic Pattern Interrupt)
# ──────────────────────────────────────────────────────────

def generate_veo_teaser(company_name: str, pagespeed_score: int) -> str:
    """
    Generates a personalized 10-second cinematic video clip using Veo 3.1.
    This acts as a high-leverage 'Pattern Interrupt' in SMS/Email.
    """
    try:
        # Initialize GenAI Client (requires VEO_PRO_KEY in environment)
        api_key = os.environ.get("VEO_PRO_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("  ⚠️ Skipping Veo teaser: No API key found")
            return None
            
        client = genai.Client(api_key=api_key)
        
        # Design the cinematic prompt
        video_prompt = (
            f"Cinematic 4k drone shot of Lakeland, Florida. "
            f"Overlay 3D glass text: '{company_name}'. "
            f"The text transitions to a glowing {'red' if pagespeed_score < 50 else 'orange'} "
            f"gauge showing {pagespeed_score}/100. "
            f"End with a digital glitch effect and the words 'We fixed this.'"
        )
        
        print(f"  🎬 Generating Veo Teaser for {company_name}...")
        
        # Trigger Generation (Async - but we wait for URL)
        video_request = client.models.generate_video(
            model="veo-3.1-ultra",
            prompt=video_prompt,
            duration_seconds=10,
            aspect_ratio="9:16" # Optimized for Mobile (SMS)
        )
        
        return video_request.url
    except Exception as e:
        print(f"  ❌ Veo Generation Failed: {e}")
        return None


# ──────────────────────────────────────────────────────────
#  PDF GENERATION (ReportLab — Traffic Light Protocol)
# ──────────────────────────────────────────────────────────

def generate_audit_pdf(
    company_name: str,
    website_url: str,
    owner_name: str,
    niche: str,
    pagespeed: dict,
    privacy: dict,
    ai_readiness: dict,
) -> bytes:
    """
    Generates a 2-3 page PDF audit report using ReportLab.
    Returns PDF as bytes.
    """
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    )

    # Color definitions (Traffic Light Protocol)
    DARK_NAVY = colors.HexColor('#1a1a2e')
    RED = colors.HexColor('#dc3545')
    LIGHT_RED = colors.HexColor('#f8d7da')
    BROWN = colors.HexColor('#856404')
    LIGHT_YELLOW = colors.HexColor('#fff3cd')
    GREEN = colors.HexColor('#155724')
    LIGHT_GREEN = colors.HexColor('#d4edda')
    WHITE = colors.white

    def status_colors(status):
        if status == "critical":
            return RED, LIGHT_RED
        elif status == "warning":
            return BROWN, LIGHT_YELLOW
        elif status == "good":
            return GREEN, LIGHT_GREEN
        else:
            return BROWN, LIGHT_YELLOW

    # PDF buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           topMargin=0.75*inch, bottomMargin=0.75*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'AuditTitle', parent=styles['Title'],
        fontSize=22, textColor=DARK_NAVY, spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'AuditSubtitle', parent=styles['Normal'],
        fontSize=12, textColor=colors.HexColor('#666666'), spaceAfter=20
    )
    heading_style = ParagraphStyle(
        'AuditHeading', parent=styles['Heading2'],
        fontSize=16, textColor=DARK_NAVY, spaceBefore=20, spaceAfter=10
    )
    body_style = ParagraphStyle(
        'AuditBody', parent=styles['Normal'],
        fontSize=11, leading=16, spaceAfter=8
    )
    critical_style = ParagraphStyle(
        'CriticalText', parent=styles['Normal'],
        fontSize=11, leading=16, textColor=RED, spaceAfter=8
    )

    story = []

    # ── PAGE 1: TITLE + EXECUTIVE SUMMARY ──
    story.append(Paragraph(f"AI Visibility Audit", title_style))
    story.append(Paragraph(f"{company_name}", ParagraphStyle(
        'CompanyName', parent=styles['Title'],
        fontSize=18, textColor=colors.HexColor('#333333'), spaceAfter=4
    )))
    story.append(Paragraph(f"Prepared for {owner_name} | {website_url}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=DARK_NAVY))
    story.append(Spacer(1, 12))

    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))

    perf_score = pagespeed.get("score", "N/A")
    perf_label = pagespeed.get("status", "unknown").upper()
    privacy_label = privacy.get("status", "critical").upper()
    ai_label = ai_readiness.get("status", "warning").upper()

    # Count critical findings
    criticals = sum(1 for s in [pagespeed["status"], privacy["status"], ai_readiness["status"]] if s == "critical")
    warnings = sum(1 for s in [pagespeed["status"], privacy["status"], ai_readiness["status"]] if s == "warning")

    if criticals > 0:
        summary_text = (
            f"Our analysis of <b>{company_name}</b> identified "
            f"<font color='#dc3545'><b>{criticals} critical issue{'s' if criticals > 1 else ''}</b></font>"
            f"{f' and {warnings} warning{chr(115) if warnings > 1 else chr(0)}' if warnings > 0 else ''} "
            f"that may be impacting your online visibility and lead generation."
        )
    else:
        summary_text = (
            f"Our analysis of <b>{company_name}</b> shows a solid foundation with "
            f"{warnings} area{'s' if warnings > 1 else ''} for improvement."
        )

    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 16))

    # ── TRAFFIC LIGHT TABLE ──
    story.append(Paragraph("Audit Results", heading_style))

    status_label = {"critical": "CRITICAL", "warning": "WARNING", "good": "GOOD", "error": "N/A", "unknown": "N/A"}

    table_data = [
        ["Area", "Status", "Finding"],
        [
            "Mobile Performance",
            status_label.get(pagespeed["status"], "N/A"),
            f"Score: {perf_score}/100 — {pagespeed.get('fcp', 'N/A')} first paint"
        ],
        [
            "Privacy Compliance",
            status_label.get(privacy["status"], "CRITICAL"),
            privacy.get("details", "No privacy policy found")
        ],
        [
            "AI Readiness",
            status_label.get(ai_readiness["status"], "WARNING"),
            ai_readiness.get("details", "No AI features detected")
        ],
    ]

    col_widths = [1.6*inch, 1.0*inch, 4.4*inch]
    table = Table(table_data, colWidths=col_widths)

    # Base table style
    table_style_commands = [
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), DARK_NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        # All cells
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]

    # Row-specific colors
    for row_idx, item in enumerate([pagespeed, privacy, ai_readiness], start=1):
        text_color, bg_color = status_colors(item["status"])
        table_style_commands.extend([
            ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color),
            ('TEXTCOLOR', (1, row_idx), (1, row_idx), text_color),
            ('FONTNAME', (1, row_idx), (1, row_idx), 'Helvetica-Bold'),
        ])

    table.setStyle(TableStyle(table_style_commands))
    story.append(table)
    story.append(Spacer(1, 20))

    # ── CRITICAL FINDING DETAIL ──
    if privacy["status"] == "critical":
        story.append(Paragraph("Critical Finding: Privacy Compliance", heading_style))
        story.append(Paragraph(
            f"<font color='#dc3545'><b>⚠ FDBR Non-Compliance Risk</b></font>",
            body_style
        ))
        story.append(Paragraph(
            f"Florida's Digital Bill of Rights (FDBR), effective July 2024, requires businesses "
            f"to maintain a clear, accessible privacy policy that discloses how consumer data is "
            f"collected, used, and shared. Our scan of <b>{website_url}</b> did not find a compliant "
            f"privacy policy page.",
            body_style
        ))
        story.append(Paragraph(
            f"<b>Potential Risk:</b> Businesses found in violation may face fines of up to "
            f"<font color='#dc3545'><b>$50,000 per incident</b></font> and loss of consumer trust.",
            critical_style
        ))
        story.append(Paragraph(
            f"<b>Our Offer:</b> As a local business courtesy, we will implement a fully compliant "
            f"FDBR privacy policy for {company_name} at <b>no charge</b>. This typically takes less "
            f"than 24 hours and requires no action from your team.",
            body_style
        ))
        story.append(Spacer(1, 12))

    # ── PERFORMANCE DETAILS ──
    if pagespeed.get("score") is not None:
        story.append(Paragraph("Performance Details", heading_style))

        perf_data = [
            ["Metric", "Value", "Target"],
            ["Mobile Score", f"{pagespeed['score']}/100", "90+"],
            ["First Contentful Paint", str(pagespeed.get("fcp", "N/A")), "< 1.8s"],
            ["Largest Contentful Paint", str(pagespeed.get("lcp", "N/A")), "< 2.5s"],
            ["Cumulative Layout Shift", str(pagespeed.get("cls", "N/A")), "< 0.1"],
            ["Speed Index", str(pagespeed.get("speed_index", "N/A")), "< 3.4s"],
        ]

        perf_table = Table(perf_data, colWidths=[2.2*inch, 2.2*inch, 2.6*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), DARK_NAVY),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (1, 1), (2, -1), 'CENTER'),
        ]))
        story.append(perf_table)
        story.append(Spacer(1, 16))

    # ── NEXT STEPS / CTA ──
    story.append(Paragraph("Recommended Next Steps", heading_style))
    story.append(Paragraph(
        f"Based on this audit, here's what we recommend for {company_name}:",
        body_style
    ))

    recommendations = []
    if privacy["status"] == "critical":
        recommendations.append(
            "<b>1. Privacy Policy (FREE):</b> Let us implement a compliant FDBR privacy policy — no cost, no obligation."
        )
    if pagespeed["status"] in ["critical", "warning"]:
        recommendations.append(
            f"<b>{'2' if recommendations else '1'}. Mobile Speed Optimization:</b> Your mobile score of {perf_score}/100 is "
            f"{'significantly ' if pagespeed['status'] == 'critical' else ''}below the recommended 90+. "
            f"We can typically improve this by 30-50 points within a week."
        )
    if ai_readiness["status"] in ["critical", "warning"]:
        recommendations.append(
            f"<b>{len(recommendations)+1}. AI-Powered Lead Capture:</b> Adding an AI assistant to your website "
            f"can capture 3-5x more leads by engaging visitors 24/7."
        )

    for rec in recommendations:
        story.append(Paragraph(rec, body_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<i>This audit was prepared by AI Service Co. | dan@aiserviceco.com</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    ))

    # Build PDF
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


# ──────────────────────────────────────────────────────────
#  MAIN: Generate Full Audit for a Lead
# ──────────────────────────────────────────────────────────

def generate_audit_for_lead(lead: dict) -> dict:
    """
    Full audit pipeline for a single lead.
    Returns dict with pdf_bytes (base64), audit_results, and email_subject/body.
    """
    company = lead.get("company_name") or "Your Company"
    website = lead.get("website_url")
    owner = (lead.get("full_name") or "Business Owner").split(" ")[0]
    niche = lead.get("niche") or "your industry"
    email = lead.get("email")

    if not website:
        return {"success": False, "error": "No website_url for this lead"}
    if not email:
        return {"success": False, "error": "No email for this lead"}

    print(f"\n🔍 AUDIT: {company} ({website})")

    # 1. Run PageSpeed Analysis
    print("  [1/3] Running PageSpeed Insights...")
    pagespeed = fetch_pagespeed(website)

    # 2. Check Privacy Policy
    print("  [2/3] Checking privacy policy...")
    privacy = check_privacy_policy(website)

    # 3. Check AI Readiness
    print("  [3/3] Checking AI readiness...")
    ai_readiness = check_ai_readiness(website)

    # 4. Generate Veo Teaser (Phase 12 Turbo)
    print("  [4/4] Generating Veo 3.1 Video Teaser...")
    video_url = generate_veo_teaser(company, pagespeed.get("score") or 0)

    # 4. Generate PDF
    print("  Generating PDF report...")
    try:
        pdf_bytes = generate_audit_pdf(
            company_name=company,
            website_url=website,
            owner_name=owner,
            niche=niche,
            pagespeed=pagespeed,
            privacy=privacy,
            ai_readiness=ai_readiness,
        )
        pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
        print(f"  PDF generated: {len(pdf_bytes)} bytes")
    except Exception as e:
        print(f"  PDF generation error: {e}")
        traceback.print_exc()
        return {"success": False, "error": f"PDF generation failed: {e}"}

    # 5. Build personalized email subject + body
    criticals = sum(1 for s in [pagespeed["status"], privacy["status"], ai_readiness["status"]] if s == "critical")

    if criticals > 0:
        subject = f"{company}: {criticals} critical issue{'s' if criticals > 1 else ''} found in your AI visibility audit"
    else:
        subject = f"{company}: Your AI visibility audit results"

    # Build HTML email body referencing the audit
    score_text = f"{pagespeed.get('score', 'N/A')}/100" if pagespeed.get("score") else "unavailable"
    privacy_text = "missing" if privacy["status"] == "critical" else "found but may need updates"

    body = f"""<html><body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; line-height: 1.6;">
<p>Hi {owner},</p>

<p>I ran a quick AI visibility audit on <b>{website}</b> and found some things worth sharing.</p>

<p><b>Key findings:</b></p>
<ul style="margin: 8px 0;">
<li>Mobile Performance Score: <b>{score_text}</b></li>
<li>Privacy Policy (FDBR Compliance): <b>{privacy_text}</b></li>
<li>AI Lead Capture: <b>{"active" if ai_readiness["status"] == "good" else "not detected"}</b></li>
</ul>

{"<p style='color: #dc3545;'><b>⚠ Important:</b> Your site appears to be missing a compliant privacy policy under Florida's Digital Bill of Rights (FDBR). This could expose " + company + " to fines of up to $50,000. I'd like to fix this for you — no cost, no catch, just a local business helping another.</p>" if privacy["status"] == "critical" else ""}

<p>I've attached the full audit report (PDF) with detailed results and recommendations.</p>

<p>Would you have 10 minutes for a quick call this week? I can walk you through the findings and we can fix the most urgent issue right away.</p>

<p>Best,<br>Dan<br><span style="color: #666; font-size: 12px;">AI Service Co. | dan@aiserviceco.com</span></p>
</body></html>"""

    # 6. Trigger Social Multiplier (Phase 13)
    try:
        from workers.social_poster import draft_social_multiplier_posts
        draft_social_multiplier_posts(lead_id=lead.get("id"))
    except Exception as e:
        print(f"  Social Multiplier trigger failed: {e}")

    return {
        "success": True,
        "pdf_b64": pdf_b64,
        "pdf_filename": f"{company.replace(' ', '_')}_AI_Audit.pdf",
        "subject": subject,
        "body": body,
        "audit_results": {
            "pagespeed": pagespeed,
            "privacy": privacy,
            "ai_readiness": ai_readiness,
            "criticals": criticals,
            "video_teaser_url": video_url,
        }
    }
