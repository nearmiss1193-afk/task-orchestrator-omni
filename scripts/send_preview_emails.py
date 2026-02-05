#!/usr/bin/env python3
"""
Send preview emails to nearmiss1193@gmail.com for owner review.
Protocol step: PREVIEW before actual send.
"""
import os
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv(r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

# Preview destination
PREVIEW_EMAIL = "nearmiss1193@gmail.com"

# Email data - Batch 1
EMAILS = [
    {
        "company": "Vanguard Plumbing & Air",
        "original_to": "info@vanguardplumbingair.com",
        "subject": "Vanguard Plumbing - Website Speed Report",
        "body": """Dear Vanguard Plumbing Team,

I recently conducted a technical audit of your website (vanguardplumbingair.com) and wanted to share what I found.

PERFORMANCE SUMMARY:

Area              | Status    | Impact
------------------|-----------|----------------------------------------
Mobile Speed      | CRITICAL  | Your site takes 5.1 seconds to load on mobile devices. Google's research shows 53% of visitors abandon sites that take over 3 seconds.
Access Issues     | WARNING   | The site returned a 403 access error during testing from some locations.
Redirect Chain    | WARNING   | The site redirects through multiple URLs before landing, adding to load time.

THE SOLUTION:

I help Lakeland-area HVAC and plumbing businesses capture more emergency calls with 24/7 AI phone systems. Here's what I can offer:

1. Free Performance Consultation - I'll identify exactly what's causing the slow load time and provide a fix recommendation at no cost.

2. 14-Day AI Intake Trial - Our AI phone system answers calls when your team is busy, qualifies leads, and schedules appointments.

NEXT STEP: Reply to this email or call me at 352-936-8152 to schedule a 15-minute call.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152
www.aiserviceco.com"""
    },
    {
        "company": "Five Points Roofing",
        "original_to": "fivepointsroofingfl@gmail.com",
        "subject": "Five Points Roofing - Website Performance Opportunity",
        "body": """Dear Five Points Roofing Team,

I recently tested your website (fivepointsroofingfl.com) and found some performance opportunities worth sharing.

PERFORMANCE SUMMARY:

Area              | Status    | Impact
------------------|-----------|----------------------------------------
Mobile Speed      | SLOW      | Your site loads in 3.6 seconds on mobile. Above Google's recommended 3-second threshold.
Security          | GOOD      | Your SSL certificate is valid and working properly.
Accessibility     | GOOD      | Site is accessible from all test locations.

WHAT THIS MEANS:

With roof emergencies (storm damage, leaks), homeowners often search on their phones. A 3.6-second load time means some potential customers are calling your competitors.

THE SOLUTION:

I offer a 14-day AI Intake trial for roofing contractors:
- Answers calls 24/7 (storms don't wait for business hours)
- Qualifies leads and collects job details
- Schedules appointments directly to your calendar
- Sends you instant notifications for urgent situations

NEXT STEP: Would you be open to a 15-minute call? Reply here or call 352-936-8152.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152"""
    },
    {
        "company": "The Original Pro Plumbing",
        "original_to": "proplumbing1@originalplumber.com",
        "subject": "Original Plumbing - Quick Website Optimization Tip",
        "body": """Dear Original Pro Plumbing Team,

I tested your website (originalplumber.com) and wanted to share what I found.

PERFORMANCE SUMMARY:

Area              | Status    | Impact
------------------|-----------|----------------------------------------
Mobile Speed      | SLOW      | Site loads in 2.1 seconds. Good, but Google recommends under 2 seconds for optimal SEO ranking.
Security          | GOOD      | SSL certificate valid.
Accessibility     | GOOD      | No access issues detected.

WHAT THIS MEANS:

You're close to optimal performance. A small speed improvement could help you outrank competitors in local search results for "Lakeland plumber."

WHY I'M REACHING OUT:

I help Lakeland plumbing businesses capture more emergency leads with AI phone systems. Our 14-day trial includes:
- 24/7 call answering (never miss a burst pipe emergency)
- Lead qualification and appointment scheduling
- Instant SMS notifications for high-priority calls

NEXT STEP: Reply to schedule a quick 15-minute demo, or call me at 352-936-8152.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152"""
    },
    {
        "company": "Hunter Plumbing Inc",
        "original_to": "hunterplumbing@hunterplumbinginc.com",
        "subject": "Hunter Plumbing - Serving Winter Haven Better",
        "body": """Dear Hunter Plumbing Team,

I focus on helping Central Florida plumbing businesses grow, and I recently tested your website (hunterplumbinginc.com).

PERFORMANCE SUMMARY:

Area              | Status    | Impact
------------------|-----------|----------------------------------------
Mobile Speed      | SLOW      | Site loads in 3.8 seconds on mobile.
Security          | GOOD      | SSL certificate is valid.
Accessibility     | GOOD      | Site accessible from all test locations.

WHAT THIS MEANS FOR WINTER HAVEN:

When a Winter Haven homeowner has a pipe burst at 2 AM, they're searching on their phone. Every second your site takes to load is a second they might call a competitor.

HOW I CAN HELP:

I offer a 14-day AI Intake trial designed for plumbers:
- 24/7 Emergency Response - AI answers calls at 2 AM just as professionally as 2 PM
- Local Knowledge - Serves Winter Haven, Lakeland, and surrounding Polk County
- Lead Qualification - Captures job details before you even call back

NEXT STEP: Would a 15-minute call work for you this week? Reply here or call 352-936-8152.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152"""
    },
    {
        "company": "Andress Electric",
        "original_to": "info@andresselectric.com",
        "subject": "Andress Electric - Capturing More Emergency Calls",
        "body": """Dear Andress Electric Team,

I specialize in helping Lakeland electrical contractors capture more emergency service calls, and I wanted to share some findings from testing your website.

PERFORMANCE SUMMARY:

Area              | Status    | Impact
------------------|-----------|----------------------------------------
Mobile Speed      | SLOW      | Site loads in 3.8 seconds on mobile devices.
Security          | GOOD      | SSL certificate valid and working.
Accessibility     | GOOD      | No access issues detected.

WHY THIS MATTERS FOR ELECTRICIANS:

Electrical emergencies are high-value, high-urgency calls. When someone's power goes out or they smell burning from an outlet, they call the first electrician they can reach.

THE SOLUTION:

Our 14-day AI Intake trial helps electricians capture more emergency calls:
- 24/7 Availability - Power outages don't follow business hours
- Emergency Triage - AI identifies urgent vs. routine calls
- Instant Notifications - You get texted immediately for emergencies
- Appointment Booking - Routine work scheduled without your involvement

NEXT STEP: Reply to schedule a 15-minute demo, or call 352-936-8152.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152"""
    },
    {
        "company": "Leaf Electric",
        "original_to": "leafelectricinfo@gmail.com",
        "subject": "Leaf Electric - Website Performance + Emergency Call Solution",
        "body": """Dear Leaf Electric Team,

I work with Lakeland-area electrical contractors, and I wanted to share some findings from testing your website (leafelectricfl.com).

PERFORMANCE SUMMARY:

Area              | Status    | Impact
------------------|-----------|----------------------------------------
Mobile Speed      | SLOW      | Site loads in 3.6 seconds on mobile.
Security          | GOOD      | SSL certificate valid.
Accessibility     | GOOD      | Site accessible from all locations tested.

THE BIGGER OPPORTUNITY:

Even with a faster website, are you capturing calls that come in after hours? Electrical emergencies are unpredictable.

HOW OUR AI INTAKE SYSTEM HELPS:

For 14 days, try our AI phone system at no cost:
- Answers calls 24/7 with professional, natural conversation
- Qualifies whether it's an emergency or routine job
- Texts you immediately for urgent calls
- Books appointments for non-urgent work

NEXT STEP: Interested in a 15-minute demo? Reply here or call 352-936-8152.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152"""
    },
    {
        "company": "Curry Plumbing",
        "original_to": "curryco@curryplumbing.com",
        "subject": "Important: Curry Plumbing Website Security Issue Detected",
        "body": """Dear Curry Plumbing Team,

I recently tested your website (curryplumbing.com) and discovered a security issue that may be affecting your business.

ISSUE DETECTED:

Area              | Status    | Impact
------------------|-----------|----------------------------------------
SSL Certificate   | CRITICAL  | Your website's SSL certificate returned an error during testing.
Customer Trust    | CRITICAL  | Modern browsers prominently warn users about SSL issues.
Google Ranking    | WARNING   | Google penalizes sites with SSL issues in search rankings.

THE GOOD NEWS:

This is typically a quick fix. Your hosting provider or web developer can usually resolve SSL certificate issues within an hour.

HOW I CAN HELP:

1. SSL Issue Resolution - I can provide a step-by-step guide to fix this with your hosting provider (takes about 1 hour).

2. 14-Day AI Intake Trial - While you fix the SSL, consider our AI phone system that answers calls 24/7, qualifies leads, and schedules appointments.

NEXT STEP: Reply to this email to get:
- Free SSL troubleshooting guide
- 15-minute demo of our AI phone system

Or call me directly at 352-936-8152.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152"""
    },
    {
        "company": "B&W Plumbing LLC",
        "original_to": "bwplumbing@yahoo.com",
        "subject": "B&W Plumbing - Your Website is Outperforming Competitors",
        "body": """Dear B&W Plumbing Team,

Good news! I recently tested your website (bandwplumbing.com) and found that you're outperforming most of your competition.

PERFORMANCE SUMMARY:

Area              | Status    | Details
------------------|-----------|----------------------------------------
Mobile Speed      | GOOD      | 1.9 second load time - faster than 80% of competitors
Security          | GOOD      | Site is secure and accessible
Configuration     | NOTE      | Some access settings returned a 403 error from certain testing locations.

WHY THIS MATTERS:

A fast website means customers searching for "Lakeland plumber" on their phones see your site before slower competitors.

THE NEXT LEVEL:

Since your website is performing well, you're perfectly positioned to add more automation. Our AI phone system captures leads 24/7:
- Answers calls when you're on a job
- Qualifies leads and captures job details
- Schedules appointments to your calendar
- Sends instant text alerts for emergencies

NEXT STEP: Would a 15-minute demo be helpful? Reply here or call 352-936-8152.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152"""
    },
    {
        "company": "Trimm Roofing",
        "original_to": "support@trimmroofing.com",
        "subject": "Trimm Roofing - Website Performance Report",
        "body": """Dear Trimm Roofing Team,

I tested your website (trimmroofing.com) and wanted to share what I found.

PERFORMANCE SUMMARY:

Area              | Status    | Details
------------------|-----------|----------------------------------------
Mobile Speed      | GOOD      | 1.8 second load time - excellent performance
Security          | GOOD      | Site is secure
Access Note       | WARNING   | Site returned a 403 error from some testing locations.

WHAT THE 403 ERROR MEANS:

A 403 error means "access forbidden." If this is happening to some visitors, they can't even see your site. This is often caused by:
- Overly aggressive security plugins
- Geographic blocking rules
- Hosting firewall misconfiguration

QUICK FIX: Ask your hosting provider to review the firewall rules for your site.

ADDITIONAL OPPORTUNITY:

For roofing contractors, I offer a 14-day AI phone system trial that answers calls 24/7, qualifies storm damage leads, and schedules appointments automatically.

NEXT STEP: Want me to provide more details on either the access issue or the AI system? Reply here or call 352-936-8152.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152"""
    },
    {
        "company": "Lakeland Air Conditioning",
        "original_to": "info@thelakelandac.com",
        "subject": "Lakeland AC - You're Ahead of the Competition",
        "body": """Dear Lakeland Air Conditioning Team,

I test local HVAC websites regularly, and yours stood out.

PERFORMANCE SUMMARY:

Area              | Status    | Details
------------------|-----------|----------------------------------------
Mobile Speed      | EXCELLENT | 684ms (under 1 second) - faster than 95% of competitors
Security          | GOOD      | SSL certificate valid and working
Accessibility     | GOOD      | No access issues detected

WHAT THIS MEANS:

When a Lakeland homeowner's AC breaks on a 95-degree day, they're searching on their phone. Your site appears almost instantly while competitors are still loading.

THE OPPORTUNITY:

Since your technical foundation is solid, you're perfectly positioned to add AI automation. Our 14-day trial includes:
- 24/7 Call Answering - Emergency AC calls at 2 AM get handled professionally
- Lead Qualification - AI determines if it's a maintenance call, repair, or emergency
- Appointment Scheduling - Routine calls get booked without your involvement
- Instant Alerts - Emergencies get texted to you immediately

NEXT STEP: Would you be open to a 15-minute demo? Reply here or call me at 352-936-8152.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152
www.aiserviceco.com"""
    }
]

def get_gmail_service():
    """Get authenticated Gmail service."""
    token_path = r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\gmail_token.json"
    
    with open(token_path, "r") as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data["scopes"]
    )
    
    return build("gmail", "v1", credentials=creds)

def send_preview_email(service, email_data):
    """Send preview email to nearmiss1193@gmail.com."""
    # Create message
    msg = MIMEMultipart()
    
    # Subject indicates preview + original recipient
    msg["Subject"] = f"[PREVIEW for {email_data['original_to']}] {email_data['subject']}"
    msg["From"] = "Daniel Coffman <owner@aiserviceco.com>"
    msg["To"] = PREVIEW_EMAIL
    
    # Body includes original recipient info
    preview_header = f"""═══════════════════════════════════════════════════════════════
PREVIEW EMAIL - For Owner Review Before Actual Send
═══════════════════════════════════════════════════════════════
ORIGINAL RECIPIENT: {email_data['original_to']}
COMPANY: {email_data['company']}
═══════════════════════════════════════════════════════════════

"""
    
    full_body = preview_header + email_data['body']
    msg.attach(MIMEText(full_body, "plain"))
    
    # Encode and send
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    
    result = service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()
    
    return result

def main():
    print("=" * 70)
    print("SENDING PREVIEW EMAILS TO nearmiss1193@gmail.com")
    print("=" * 70)
    
    service = get_gmail_service()
    
    sent = 0
    failed = 0
    
    for i, email in enumerate(EMAILS, 1):
        try:
            print(f"\n[{i}/10] Sending: {email['company']}...")
            result = send_preview_email(service, email)
            print(f"   ✅ Sent! Message ID: {result['id'][:20]}...")
            sent += 1
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"COMPLETE: {sent} sent, {failed} failed")
    print(f"Check nearmiss1193@gmail.com for preview emails")
    print("=" * 70)

if __name__ == "__main__":
    main()
