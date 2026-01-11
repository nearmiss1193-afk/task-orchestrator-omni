"""
FOLLOW-UP SCHEDULER
===================
Runs daily to check which leads need their next touch.
Implements the 14-day multi-touch cadence.
"""
import os
import json
import requests
import re
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Config
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
VAPI_PHONE_ID = 'ee668638-38f0-4984-81ae-e2fd5d83084b'
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"
GHL_WEBHOOK_URL = os.getenv('GHL_SMS_WEBHOOK_URL')
RESEND_API_KEY = os.getenv('RESEND_API_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

logging.basicConfig(
    filename='followup_scheduler_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Touch schedule
TOUCH_SCHEDULE = {
    1: {"channels": ["email", "call"], "next_day": 3},
    3: {"channels": ["call"], "next_day": 4},
    4: {"channels": ["email"], "next_day": 7},
    7: {"channels": ["sms"], "next_day": 10},
    10: {"channels": ["call", "email"], "next_day": 14},
    14: {"channels": ["email"], "next_day": None},  # End of sequence
}

def get_leads_needing_followup():
    """Get all leads that need their next touch today."""
    try:
        result = supabase.table("leads").select("*").execute()
        today = datetime.now().date()
        leads_to_follow_up = []
        
        for lead in result.data:
            research = lead.get('agent_research', {})
            if isinstance(research, str):
                try:
                    research = json.loads(research)
                except:
                    continue
            
            # Check if this is a multitouch lead
            if research.get('source') != 'Empire_MultiTouch':
                continue
            
            first_contact = research.get('first_contact')
            if not first_contact:
                continue
            
            current_touch = research.get('current_touch', 1)
            next_touch = TOUCH_SCHEDULE.get(current_touch, {}).get('next_day')
            
            if next_touch is None:
                continue  # Sequence complete
            
            # Calculate when next touch is due
            first_contact_date = datetime.fromisoformat(first_contact.replace('Z', '+00:00')).date()
            next_touch_date = first_contact_date + timedelta(days=next_touch - 1)
            
            if next_touch_date == today:
                leads_to_follow_up.append({
                    'email': lead['email'],
                    'research': research,
                    'next_touch': next_touch
                })
        
        return leads_to_follow_up
        
    except Exception as e:
        logger.error(f"Error getting followup leads: {e}")
        return []

def send_touch(lead_data, touch_day):
    """Execute the touch for the specified day."""
    research = lead_data['research']
    company = research.get('company_name', 'Unknown')
    phone = research.get('phone', '')
    city = research.get('city', '')
    state = research.get('state', '')
    
    touch = TOUCH_SCHEDULE.get(touch_day, {})
    channels = touch.get('channels', [])
    
    success = False
    
    for channel in channels:
        if channel == 'email':
            # Send email
            try:
                import resend
                resend.api_key = RESEND_API_KEY
                
                template = get_email_template(touch_day, company, city, state)
                resend.Emails.send({
                    "from": "sarah@aiserviceco.com",
                    "to": [lead_data['email']],
                    "subject": template['subject'],
                    "text": template['body']
                })
                logger.info(f"EMAIL Day{touch_day}: {company}")
                success = True
            except Exception as e:
                logger.warning(f"Email failed: {e}")
        
        elif channel == 'call':
            # Make call
            try:
                res = requests.post(
                    "https://api.vapi.ai/call",
                    headers={"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"},
                    json={
                        "type": "outboundPhoneCall",
                        "phoneNumberId": VAPI_PHONE_ID,
                        "assistantId": ASSISTANT_ID,
                        "customer": {"number": phone, "name": company}
                    },
                    timeout=15
                )
                if res.status_code == 201:
                    logger.info(f"CALL Day{touch_day}: {company}")
                    success = True
            except:
                pass
        
        elif channel == 'sms':
            # Send SMS via GHL
            try:
                message = f"Hi! Sarah from AI Service Co. Following up about automating calls at {company}. Still interested? Text YES!"
                requests.post(GHL_WEBHOOK_URL, json={
                    "phone": phone,
                    "message": message,
                    "source": "Empire_FollowUp"
                }, timeout=10)
                logger.info(f"SMS Day{touch_day}: {company}")
                success = True
            except:
                pass
    
    # Update lead status
    if success:
        try:
            research['current_touch'] = touch_day
            history = research.get('outreach_history', [])
            history.append({
                'day': touch_day,
                'date': datetime.now().isoformat(),
                'channels': channels
            })
            research['outreach_history'] = history
            
            supabase.table("leads").update({
                'status': f'touch_{touch_day}',
                'agent_research': json.dumps(research)
            }).eq('email', lead_data['email']).execute()
            
        except Exception as e:
            logger.warning(f"Status update failed: {e}")
    
    return success

def get_email_template(touch_day, company, city, state):
    templates = {
        3: {
            "subject": f"Following up - {company}",
            "body": f"Hi,\n\nJust following up on my call earlier. I know HVAC season keeps you busy in {city}!\n\nQuick question: Are you currently missing calls during jobs or after hours?\n\nOur AI answers 24/7 and books appointments automatically. Worth a quick chat?\n\nSarah\nAI Service Company\n(863) 260-8351"
        },
        4: {
            "subject": f"Case study for {company}",
            "body": f"Hi,\n\nThought you might find this interesting - a company like yours in {state} increased their booked jobs by 40% after our AI started handling their calls.\n\nThe difference? No more missed calls at night, on weekends, or during jobs.\n\nWant to see how it works?\n\nSarah"
        },
        7: {
            "subject": f"Quick check-in - {company}",
            "body": f"Hi,\n\nJust checking in. Have you had a chance to think about automating your customer calls at {company}?\n\nHappy to answer any questions.\n\nSarah\n(863) 260-8351"
        },
        10: {
            "subject": f"Special offer for {company}",
            "body": f"Hi,\n\nI've been trying to connect about helping {company} with automated customer calls.\n\nThis week only: FREE 30-day trial, no credit card required.\n\nIf you're losing even 2-3 calls per week to voicemail, our AI could be booking those jobs for you instead.\n\nWant me to set it up?\n\nSarah\nAI Service Company"
        },
        14: {
            "subject": f"Closing your file - {company}",
            "body": f"Hi,\n\nI've sent a few messages about helping {company} automate customer communications.\n\nSince I haven't heard back, I'll close your file. If anything changes, you can reach me at (863) 260-8351.\n\nWishing {company} continued success!\n\nSarah"
        }
    }
    return templates.get(touch_day, templates[7])

def main():
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║      FOLLOW-UP SCHEDULER                                 ║
║      Checking leads for today's touches...               ║
╚═══════════════════════════════════════════════════════════╝
""")
    logger.info("Follow-up scheduler started")
    
    leads = get_leads_needing_followup()
    print(f"Found {len(leads)} leads needing follow-up today")
    
    processed = 0
    for lead in leads:
        company = lead['research'].get('company_name', 'Unknown')
        touch_day = lead['next_touch']
        
        print(f"  Processing Day {touch_day} touch: {company}")
        
        if send_touch(lead, touch_day):
            processed += 1
            print(f"    ✅ Complete")
        else:
            print(f"    ❌ Failed")
        
        time.sleep(60)  # 1 min between follow-ups
    
    print(f"\n✅ Processed {processed}/{len(leads)} follow-ups")
    logger.info(f"Processed {processed}/{len(leads)} follow-ups")

if __name__ == "__main__":
    main()
