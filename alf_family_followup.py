"""
FAMILY FOLLOW-UP SEQUENCES
==========================
Nurture undecided ALF families.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
RESEND_API_KEY = os.getenv('RESEND_API_KEY')

# Follow-up sequence for ALF families
ALF_SEQUENCE = [
    {
        "day": 1,
        "channel": "sms",
        "message": "Hi {name}, it was great speaking with you about care options for {senior}. Let me know if any questions come up! - Sarah, Seacoast ALF Referrals"
    },
    {
        "day": 3,
        "channel": "sms",
        "message": "Hi {name}, just checking in. Have you had a chance to discuss the facilities we talked about? Happy to answer any questions!"
    },
    {
        "day": 5,
        "channel": "email",
        "subject": "Resources for Your Senior Care Decision",
        "message": """Hi {name},

I know this is a big decision, and I wanted to share some resources that might help:

📋 **Questions to Ask During Tours:**
- What's the staff-to-resident ratio?
- How do you handle medical emergencies?
- What activities are available?
- Can I see a sample meal menu?

📍 **The facilities we discussed:**
{facilities_list}

I'm here to help make this process easier. Would you like me to schedule some tours for you?

Warmly,
Sarah
Seacoast ALF Referrals
(863) 213-2505"""
    },
    {
        "day": 7,
        "channel": "sms",
        "message": "Hi {name}, I haven't heard from you in a few days. No pressure at all - just want you to know I'm here when you're ready. 🙏"
    },
    {
        "day": 14,
        "channel": "email",
        "subject": "Still thinking about senior care?",
        "message": """Hi {name},

I know finding the right care for {senior} is a big decision. Many families need time to process, and that's completely okay.

When you're ready, I can help with:
✅ Scheduling private tours
✅ Understanding pricing and payment options
✅ Navigating Medicaid/Medicare
✅ Finding the right care level

Just reply to this email or call me at (863) 213-2505.

Here for you,
Sarah"""
    },
    {
        "day": 21,
        "channel": "sms",
        "message": "Hi {name}, just a gentle check-in. Circumstances change - if you need help with {senior}'s care, I'm just a call away. No pressure ever. 💙"
    }
]


def enroll_family(family: dict, facilities_discussed: list = None) -> dict:
    """Enroll a family in the nurture sequence"""
    
    enrollment = {
        "family_id": f"FAM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "family": family,
        "facilities_discussed": facilities_discussed or [],
        "enrolled_at": datetime.now().isoformat(),
        "current_step": 0,
        "status": "active",
        "steps_completed": []
    }
    
    save_enrollment(enrollment)
    print(f"[ALF] Enrolled {family.get('name')} in nurture sequence")
    
    return enrollment


def save_enrollment(enrollment: dict):
    """Save enrollment to file"""
    os.makedirs("alf_enrollments", exist_ok=True)
    filename = f"alf_enrollments/{enrollment['family_id']}.json"
    with open(filename, "w") as f:
        json.dump(enrollment, f, indent=2)


def execute_step(enrollment: dict, step_index: int):
    """Execute a follow-up step"""
    
    if step_index >= len(ALF_SEQUENCE):
        return {"status": "sequence_complete"}
    
    step = ALF_SEQUENCE[step_index]
    family = enrollment['family']
    
    # Personalize message
    facilities_list = "\n".join([f"- {f}" for f in enrollment.get('facilities_discussed', [])])
    
    message = step['message'].format(
        name=family.get('contact', family.get('name', 'there')).split()[0],
        senior=family.get('senior_name', 'your loved one'),
        facilities_list=facilities_list or "- (Let me know if you'd like recommendations!)"
    )
    
    result = {"step": step_index, "channel": step['channel'], "executed_at": datetime.now().isoformat()}
    
    if step['channel'] == 'sms' and family.get('phone'):
        try:
            requests.post(GHL_SMS_WEBHOOK, json={"phone": family['phone'], "message": message})
            result["sent"] = True
            print(f"[ALF] SMS sent to {family.get('name')}")
        except Exception as e:
            result["sent"] = False
            result["error"] = str(e)
    
    elif step['channel'] == 'email' and family.get('email') and RESEND_API_KEY:
        try:
            response = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
                json={
                    "from": "Sarah <sarah@aiserviceco.com>",
                    "to": [family['email']],
                    "subject": step['subject'].format(name=family.get('name', 'there')),
                    "text": message
                }
            )
            result["sent"] = response.status_code == 200
            print(f"[ALF] Email sent to {family.get('name')}")
        except Exception as e:
            result["sent"] = False
            result["error"] = str(e)
    
    return result


def check_due_steps():
    """Check all enrollments for due steps"""
    
    os.makedirs("alf_enrollments", exist_ok=True)
    
    for filename in os.listdir("alf_enrollments"):
        if not filename.endswith('.json'):
            continue
        
        with open(f"alf_enrollments/{filename}") as f:
            enrollment = json.load(f)
        
        if enrollment.get('status') != 'active':
            continue
        
        current_step = enrollment.get('current_step', 0)
        if current_step >= len(ALF_SEQUENCE):
            enrollment['status'] = 'completed'
            save_enrollment(enrollment)
            continue
        
        # Check if step is due
        enrolled_at = datetime.fromisoformat(enrollment['enrolled_at'])
        step = ALF_SEQUENCE[current_step]
        due_date = enrolled_at + timedelta(days=step['day'])
        
        if datetime.now() >= due_date:
            result = execute_step(enrollment, current_step)
            enrollment['steps_completed'].append(result)
            enrollment['current_step'] = current_step + 1
            save_enrollment(enrollment)


if __name__ == "__main__":
    # Test
    test_family = {
        "name": "Johnson Family",
        "contact": "Mary Johnson",
        "phone": "+13529368152",
        "email": "mary@example.com",
        "senior_name": "Robert"
    }
    
    enrollment = enroll_family(test_family, ["Sunrise Senior Living", "Brookdale Tampa"])
    
    # Execute first step immediately for testing
    result = execute_step(enrollment, 0)
    print(json.dumps(result, indent=2))
