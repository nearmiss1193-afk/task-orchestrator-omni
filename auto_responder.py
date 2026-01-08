"""
AUTO-RESPONDER (Phase 11)
=========================
Automated email replies for common queries.
Uses AI to generate contextual responses based on templates.
"""
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from modules.email_command import EmailCommander
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Response Templates
TEMPLATES = {
    "quote_request": {
        "keywords": ["quote", "estimate", "price", "cost", "how much"],
        "subject": "Re: Your Quote Request - AI Service Company",
        "body": """Hi there!

Thank you for reaching out to AI Service Company!

We'd be happy to provide you with a free quote. To give you the most accurate estimate, could you please share:

1. The type of service you need (HVAC, Plumbing, Roofing, etc.)
2. Your location (City/Zip Code)
3. A brief description of the issue or project

Alternatively, you can call us directly at 1-352-758-5336 and speak with Sarah, our AI assistant, who can help you 24/7.

Looking forward to helping you!

Best regards,
The AI Service Company Team
https://aiserviceco.com
"""
    },
    "appointment": {
        "keywords": ["appointment", "schedule", "book", "available", "when can"],
        "subject": "Re: Scheduling Your Appointment - AI Service Company",
        "body": """Hi!

Thanks for wanting to schedule with us!

You can book an appointment instantly by:
1. Calling 1-352-758-5336 (Sarah will help you find the perfect time)
2. Visiting our website: https://aiserviceco.com

We have availability this week! What day works best for you?

Best regards,
The AI Service Company Team
"""
    },
    "general_inquiry": {
        "keywords": ["question", "help", "information", "inquiry", "wondering"],
        "subject": "Re: Your Inquiry - AI Service Company",
        "body": """Hello!

Thank you for contacting AI Service Company!

We received your message and will get back to you within 24 hours. For immediate assistance, please call us at 1-352-758-5336.

Our services include:
- HVAC (Heating, Ventilation, Air Conditioning)
- Plumbing
- Roofing
- And more!

Best regards,
The AI Service Company Team
https://aiserviceco.com
"""
    }
}

def log_to_superbrain(level, message, metadata=None):
    """Log events to system_logs table."""
    try:
        if SUPABASE_URL and SUPABASE_KEY:
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            client.table('system_logs').insert({
                'level': level,
                'message': message,
                'metadata': metadata or {},
                'created_at': datetime.now().isoformat()
            }).execute()
    except Exception as e:
        print(f"Log error: {e}")

def detect_intent(email):
    """Detect the intent of an email to select appropriate template."""
    text = (email.get('subject', '') + ' ' + email.get('snippet', '')).lower()
    
    for intent, template in TEMPLATES.items():
        for keyword in template['keywords']:
            if keyword in text:
                return intent
    
    return "general_inquiry"  # Default fallback

def should_auto_respond(email):
    """Determine if we should auto-respond to this email."""
    sender = email.get('from', '').lower()
    
    # Don't respond to no-reply addresses
    if 'no-reply' in sender or 'noreply' in sender:
        return False
    
    # Don't respond to our own emails
    if 'aiserviceco.com' in sender:
        return False
    
    # Don't respond to obvious spam
    spam_indicators = ['unsubscribe', 'newsletter', 'promotion', 'advertisement']
    subject = email.get('subject', '').lower()
    if any(spam in subject for spam in spam_indicators):
        return False
    
    return True

def process_and_respond(dry_run=True):
    """Process unread emails and send auto-responses."""
    print(f"🤖 [{datetime.now().strftime('%H:%M:%S')}] Auto-Responder Running...")
    
    try:
        commander = EmailCommander()
        
        if not commander.service:
            print("   ❌ Gmail auth failed")
            return
        
        emails = commander.get_unread_emails(10)
        
        if not emails:
            print("   No unread emails to process.")
            return
        
        print(f"   Found {len(emails)} unread emails.")
        responses_sent = 0
        
        for email in emails:
            if not should_auto_respond(email):
                print(f"   ⏭️  Skipping: {email['from'][:30]}")
                continue
            
            intent = detect_intent(email)
            template = TEMPLATES[intent]
            
            # Extract reply-to address
            sender_email = email['from']
            match = re.search(r'<(.+?)>', sender_email)
            reply_to = match.group(1) if match else sender_email
            
            print(f"   📧 Intent: {intent} | To: {reply_to[:30]}...")
            
            if dry_run:
                print(f"      [DRY RUN] Would send: {template['subject']}")
            else:
                success = commander.send_email(
                    to=reply_to,
                    subject=template['subject'],
                    body=template['body']
                )
                
                if success:
                    responses_sent += 1
                    commander.mark_as_read(email['id'])
                    log_to_superbrain('INFO', f'Auto-response sent: {intent}', {
                        'to': reply_to,
                        'intent': intent
                    })
        
        print(f"   ✅ Complete. {responses_sent} responses sent.")
        
    except Exception as e:
        log_to_superbrain('ERROR', f'Auto-responder failed: {str(e)}')
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    # Run in dry-run mode by default for safety
    print("Running in DRY RUN mode (no emails will be sent)")
    print("To send real emails, call: process_and_respond(dry_run=False)")
    process_and_respond(dry_run=True)
