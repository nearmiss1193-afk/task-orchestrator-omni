"""
EMAIL INBOX READER
==================
Reads and displays recent emails from the business inbox.
Allows the AI to understand, analyze, and recommend actions.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.email_command import EmailCommander
from datetime import datetime

def read_inbox():
    """Read and display recent emails with analysis."""
    print("=" * 60)
    print("📬 BUSINESS EMAIL INBOX REPORT")
    print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    commander = EmailCommander()
    
    if not commander.service:
        print("❌ Gmail not authenticated. Run modules/email_command.py first.")
        return
    
    emails = commander.get_unread_emails(15)
    
    if not emails:
        print("\n✅ No unread emails in inbox.")
        return []
    
    print(f"\n📨 Found {len(emails)} unread email(s):\n")
    
    email_data = []
    
    for i, email in enumerate(emails, 1):
        sender = email.get('from', 'Unknown')
        subject = email.get('subject', 'No Subject')
        snippet = email.get('snippet', '')[:150]
        date = email.get('date', '')
        body = email.get('body', '')[:500]
        
        # Categorize email
        category = categorize_email(subject, snippet, sender)
        
        print(f"─── Email {i} ───────────────────────────────────")
        print(f"📧 From: {sender}")
        print(f"📌 Subject: {subject}")
        print(f"📅 Date: {date}")
        print(f"🏷️  Category: {category}")
        print(f"📝 Preview: {snippet}...")
        print()
        
        email_data.append({
            'id': email.get('id'),
            'from': sender,
            'subject': subject,
            'category': category,
            'snippet': snippet,
            'body': body,
            'date': date
        })
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY & RECOMMENDED ACTIONS")
    print("=" * 60)
    
    categories = {}
    for e in email_data:
        cat = e['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in categories.items():
        action = get_action_for_category(cat)
        print(f"  {cat}: {count} email(s) → {action}")
    
    print()
    return email_data

def categorize_email(subject, body, sender):
    """Categorize email by content."""
    text = (subject + ' ' + body + ' ' + sender).lower()
    
    # Lead / Business Inquiry
    if any(kw in text for kw in ['quote', 'estimate', 'price', 'service', 'interested', 'hvac', 'plumbing', 'roofing']):
        return "🎯 LEAD"
    
    # Payment / Invoice
    if any(kw in text for kw in ['payment', 'invoice', 'paid', 'stripe', 'receipt']):
        return "💰 PAYMENT"
    
    # System Alert
    if any(kw in text for kw in ['alert', 'failure', 'error', 'modal', 'vercel', 'supabase']):
        return "⚠️ SYSTEM ALERT"
    
    # Newsletter / Marketing
    if any(kw in text for kw in ['unsubscribe', 'newsletter', 'marketing', 'promo']):
        return "📰 NEWSLETTER"
    
    # Calendar / Scheduling
    if any(kw in text for kw in ['calendar', 'meeting', 'schedule', 'appointment', 'reminder']):
        return "📅 CALENDAR"
    
    # Social / Notifications
    if any(kw in text for kw in ['linkedin', 'twitter', 'facebook', 'instagram']):
        return "📱 SOCIAL"
    
    return "📧 GENERAL"

def get_action_for_category(category):
    """Recommend action for each category."""
    actions = {
        "🎯 LEAD": "Respond ASAP with quote/info",
        "💰 PAYMENT": "Verify & acknowledge",
        "⚠️ SYSTEM ALERT": "Investigate & fix",
        "📰 NEWSLETTER": "Archive or unsubscribe",
        "📅 CALENDAR": "Confirm or decline",
        "📱 SOCIAL": "Review engagement",
        "📧 GENERAL": "Review manually"
    }
    return actions.get(category, "Review")

if __name__ == "__main__":
    emails = read_inbox()
