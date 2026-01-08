"""
OUTREACH SEQUENCE SCHEDULER
===========================
Automates follow-up sequences: Day 1 email, Day 3 call, Day 7 breakup.
"""

import os
import json
import schedule
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
import subprocess

load_dotenv()

SEQUENCES_FILE = "active_sequences.json"
GHL_SMS_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"

# Sequence templates
SEQUENCES = {
    "hvac_outreach": [
        {"day": 0, "action": "email", "template": "initial"},
        {"day": 1, "action": "sms", "message": "Hey {{name}}, just sent you an email about AI for your HVAC business. Worth a quick look?"},
        {"day": 3, "action": "call", "type": "follow_up"},
        {"day": 5, "action": "email", "template": "follow_up"},
        {"day": 7, "action": "sms", "message": "Last note - would you take a 5 min call to see how we help HVAC companies catch missed calls?"},
        {"day": 10, "action": "email", "template": "breakup"}
    ]
}


def load_sequences():
    """Load active sequences from file"""
    try:
        with open(SEQUENCES_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_sequences(sequences: list):
    """Save active sequences to file"""
    with open(SEQUENCES_FILE, "w") as f:
        json.dump(sequences, f, indent=2)


def enroll_prospect(prospect: dict, sequence_name: str = "hvac_outreach"):
    """Enroll a prospect in a sequence"""
    sequences = load_sequences()
    
    if sequence_name not in SEQUENCES:
        print(f"[ERROR] Unknown sequence: {sequence_name}")
        return
    
    enrollment = {
        "prospect": prospect,
        "sequence": sequence_name,
        "enrolled_at": datetime.now().isoformat(),
        "current_step": 0,
        "status": "active",
        "steps_completed": []
    }
    
    sequences.append(enrollment)
    save_sequences(sequences)
    print(f"[ENROLLED] {prospect.get('name')} in {sequence_name}")
    
    # Execute first step immediately
    execute_step(enrollment, 0)


def execute_step(enrollment: dict, step_index: int):
    """Execute a specific step in the sequence"""
    sequence = SEQUENCES.get(enrollment['sequence'], [])
    
    if step_index >= len(sequence):
        enrollment['status'] = 'completed'
        print(f"[COMPLETE] Sequence finished for {enrollment['prospect'].get('name')}")
        return
    
    step = sequence[step_index]
    prospect = enrollment['prospect']
    
    print(f"[STEP {step_index}] {step['action']} for {prospect.get('name')}")
    
    if step['action'] == 'email':
        send_sequence_email(prospect, step.get('template'))
    elif step['action'] == 'sms':
        send_sequence_sms(prospect, step.get('message'))
    elif step['action'] == 'call':
        trigger_sequence_call(prospect, step.get('type'))
    
    enrollment['steps_completed'].append({
        "step": step_index,
        "action": step['action'],
        "executed_at": datetime.now().isoformat()
    })
    enrollment['current_step'] = step_index + 1


def send_sequence_email(prospect: dict, template: str):
    """Send email as part of sequence"""
    print(f"[EMAIL] Sending {template} email to {prospect.get('email')}")
    # Would call hvac_campaign.py email logic here


def send_sequence_sms(prospect: dict, message: str):
    """Send SMS as part of sequence"""
    phone = prospect.get('phone')
    if not phone:
        print(f"[SKIP] No phone for {prospect.get('name')}")
        return
    
    # Personalize message
    personalized = message.replace("{{name}}", prospect.get('name', 'there'))
    
    try:
        requests.post(GHL_SMS_WEBHOOK, json={
            "phone": phone,
            "message": personalized
        })
        print(f"[SMS] Sent to {phone}")
    except Exception as e:
        print(f"[ERROR] SMS failed: {e}")


def trigger_sequence_call(prospect: dict, call_type: str):
    """Trigger Sarah call as part of sequence"""
    phone = prospect.get('phone')
    if not phone:
        print(f"[SKIP] No phone for {prospect.get('name')}")
        return
    
    try:
        result = subprocess.run(
            ["python", "call_sara_prospect.py", "--phone", phone],
            capture_output=True, text=True, timeout=30
        )
        print(f"[CALL] Triggered for {phone}")
    except Exception as e:
        print(f"[ERROR] Call trigger failed: {e}")


def check_due_steps():
    """Check for due sequence steps and execute them"""
    sequences = load_sequences()
    now = datetime.now()
    
    for enrollment in sequences:
        if enrollment['status'] != 'active':
            continue
        
        sequence = SEQUENCES.get(enrollment['sequence'], [])
        current_step = enrollment['current_step']
        
        if current_step >= len(sequence):
            enrollment['status'] = 'completed'
            continue
        
        step = sequence[current_step]
        enrolled_at = datetime.fromisoformat(enrollment['enrolled_at'])
        due_date = enrolled_at + timedelta(days=step['day'])
        
        if now >= due_date:
            execute_step(enrollment, current_step)
    
    save_sequences(sequences)


def get_sequence_status():
    """Get status of all active sequences"""
    sequences = load_sequences()
    return {
        "total": len(sequences),
        "active": len([s for s in sequences if s['status'] == 'active']),
        "completed": len([s for s in sequences if s['status'] == 'completed']),
        "sequences": sequences
    }


def run_scheduler():
    """Run the sequence scheduler"""
    print("[SCHEDULER] Starting outreach sequence scheduler...")
    print("[SCHEDULER] Checking for due steps every 15 minutes")
    
    schedule.every(15).minutes.do(check_due_steps)
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            print(json.dumps(get_sequence_status(), indent=2))
        elif sys.argv[1] == "check":
            check_due_steps()
        elif sys.argv[1] == "enroll":
            # Example: python sequence_scheduler.py enroll "Company" "email" "phone"
            if len(sys.argv) >= 5:
                prospect = {
                    "name": sys.argv[2],
                    "email": sys.argv[3],
                    "phone": sys.argv[4]
                }
                enroll_prospect(prospect)
    else:
        run_scheduler()
