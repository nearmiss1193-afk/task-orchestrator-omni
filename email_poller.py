"""
EMAIL POLLER (Phase 11)
=======================
Cron job that checks Gmail inbox every 15 minutes.
Parses leads, logs to Supabase system_logs, and triggers follow-up actions.
"""
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import our email commander
from modules.email_command import EmailCommander

# Supabase for logging
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

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

def extract_lead_info(email):
    """Extract potential lead information from email."""
    lead = {
        'email_id': email.get('id'),
        'from': email.get('from', ''),
        'subject': email.get('subject', ''),
        'body_preview': email.get('snippet', '')[:200],
        'is_lead': False,
        'lead_type': None
    }
    
    # Lead detection patterns
    lead_keywords = [
        'quote', 'estimate', 'price', 'cost', 'service',
        'appointment', 'schedule', 'book', 'consultation',
        'hvac', 'plumbing', 'repair', 'install', 'fix',
        'contact', 'inquiry', 'interested', 'help'
    ]
    
    text_to_check = (lead['subject'] + ' ' + lead['body_preview']).lower()
    
    for keyword in lead_keywords:
        if keyword in text_to_check:
            lead['is_lead'] = True
            lead['lead_type'] = keyword
            break
    
    # Extract phone numbers
    phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
    phones = re.findall(phone_pattern, email.get('body', '') or email.get('snippet', ''))
    if phones:
        lead['phone'] = phones[0]
    
    return lead

def poll_inbox():
    """Main polling function."""
    print(f"📬 [{datetime.now().strftime('%H:%M:%S')}] Polling inbox...")
    
    try:
        commander = EmailCommander()
        
        if not commander.service:
            log_to_superbrain('ERROR', 'Email poller: Gmail auth failed')
            return
        
        emails = commander.get_unread_emails(20)
        
        if not emails:
            print("   No unread emails.")
            log_to_superbrain('INFO', 'Email poll: No new emails')
            return
        
        print(f"   Found {len(emails)} unread emails.")
        leads_found = 0
        
        for email in emails:
            lead = extract_lead_info(email)
            
            if lead['is_lead']:
                leads_found += 1
                print(f"   🎯 LEAD DETECTED: {lead['from']} - {lead['subject']}")
                
                # Log to Super Brain
                log_to_superbrain('LEAD', f"New lead from {lead['from']}", lead)
                
                # Mark as read to avoid re-processing
                commander.mark_as_read(email['id'])
            else:
                print(f"   📧 Regular: {lead['from'][:30]} - {lead['subject'][:40]}")
        
        log_to_superbrain('INFO', f'Email poll complete: {len(emails)} emails, {leads_found} leads')
        print(f"   ✅ Poll complete. {leads_found} leads logged.")
        
    except Exception as e:
        log_to_superbrain('ERROR', f'Email poller failed: {str(e)}')
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    poll_inbox()
