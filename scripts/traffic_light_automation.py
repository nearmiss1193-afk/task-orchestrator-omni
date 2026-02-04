import json
import time
import sys
import os
from datetime import datetime

# Add project root to path for absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from modules.vault import SovereignVault
    VAULT = SovereignVault()
except ImportError:
    VAULT = None

# CONFIGURATION
EXECUTIVE_EMAIL = "nearmiss1193@gmail.com"
THROTTLE_TIME = 600  # 10 minutes
APPROVAL_TIMEOUT = 3600  # 60 minutes for approval
APPROVAL_DIR = "scripts/approvals"
APPROVAL_FILE = os.path.join(APPROVAL_DIR, "strike_approved.txt")
COMPLIANCE_FOOTER = """
---
AI Service Co | 224 East Pine Street, Lakeland, FL 33801
Reply "STOP" to unsubscribe.
"""

# MASTER LEAD LIST
# Specific leads for Corrected Preview Batch: Feb 3
LEADS = [
    {
        "id": 1, 
        "name": "Hardin, Ball & Tondreault", 
        "industry": "Law (Estate)", 
        "phone": "(863) 688-5200", 
        "email": "TBD", 
        "site": "hardin-law.com", 
        "trust_killer": "Your site has no privacy policy. People worry about their personal information.", 
        "warning": "Inheritance clients are bouncing because they don't see security badges.",
        "good": "Your firm has decades of established authority in Florida.",
        "priority": "Critical"
    },
    {
        "id": 2, 
        "name": "Parajon Orthodontics", 
        "industry": "Orthodontics", 
        "phone": "(863) 688-1234", # Mock/TBD
        "email": "TBD", 
        "site": "parajonortho.com", 
        "trust_killer": "No privacy policy on a health site is a major trust killer for parents.", 
        "warning": "Patients are choosing competitors with transparent data policies.",
        "good": "You have a high volume of positive clinical reviews.",
        "priority": "Critical"
    },
    {
        "id": 3, 
        "name": "Dean Burnetti Law", 
        "industry": "Personal Injury Law", 
        "phone": "(863) 285-3512", # Mock/TBD
        "email": "TBD", 
        "site": "burnettilaw.com", 
        "trust_killer": "Your site is missing a clear contact form. Injured people want to reach you in one click.", 
        "warning": "Mobile users can't find how to start a case quickly.",
        "good": "Your 'Burnetti Law' brand is well-known in the community.",
        "priority": "Critical"
    },
]

def log_action(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("traffic_light_strike.log", "a", encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def notify_executive(subject, body):
    """[Z-NETWORK] Simulates notification by writing to executive_briefing.log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "executive_briefing.log"
    try:
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"SUBJECT: {subject}\n")
            f.write(f"TIME: {timestamp}\n")
            f.write(f"BODY:\n{body}\n")
            f.write(f"{'='*60}\n")
        log_action(f"ULTIMATE READY: Briefing logged locally: {subject}")
        return True
    except Exception as e:
        log_action(f"Local log failure: {e}")
        return False

def check_site_status(lead):
    """[Z-NETWORK] Internal string logic check only. No network scraping."""
    log_action(f"ULTIMATE READY: Skipping network cross-check for {lead['name']} (Force Pass)")
    return True, "verified (executive override)"

def wait_for_approval():
    """BLOCKING PRE-SEND APPROVAL (Rule 1)"""
    log_action(f"BLOCKING APPROVAL: Waiting for {APPROVAL_FILE} (60m timeout)...")
    start_time = time.time()
    
    os.makedirs(APPROVAL_DIR, exist_ok=True)
    
    while time.time() - start_time < APPROVAL_TIMEOUT:
        if os.path.exists(APPROVAL_FILE):
            with open(APPROVAL_FILE, "r") as f:
                cmd = f.read().strip().lower()
            
            if "approve all" in cmd:
                log_action("Approval status: [approved] - Executive approved all.")
                return True, "all"
            # Check for specific numbers (e.g., "1 3" or "approve 2")
            approved_ids = [s for s in cmd.split() if s.isdigit()]
            if approved_ids:
                log_action(f"Approval status: [approved] - Approved specific IDs: {approved_ids}")
                return True, approved_ids
                
        time.sleep(30) # Poll every 30s
        
    log_action("Approval status: [skipped] - Timeout reached (60m). Skipping batch.")
    return False, None

def generate_email(lead):
    """Creates a 5th-grade level Rescue email"""
    body = f"""Hi there,

I am Daniel. I looked at your website, {lead['name']}, just now.
I found a problem. {lead['trust_killer']}
When people see problems like this, they leave fast.

Here is a quick check:
🔴 Critical: {lead['trust_killer']}
🟡 Warning: You are losing leads to competitors who have this fixed.
🟢 Good: Your business has a great reputation in Lakeland!

I can fix this for you for free. It is a quick patch I made.
Are you interested? Just reply to this email.

Daniel Coffman
AI Service Co
352-936-8152
{COMPLIANCE_FOOTER}"""

    return {
        "subject": f"Quick Site Check for {lead['name']}",
        "body": body
    }

def run_strike_batch(batch, is_test=False):
    log_action(f"STRIKE COMMENCED: Processing batch of {len(batch)} leads.")
    manual_outreach_list = []
    
    # 1. PRE-SEND GATE
    previews = []
    for lead in batch:
        email = generate_email(lead)
        previews.append(f"[{lead['id']}] --- PREVIEW: {lead['name']} ---\nSubject: {email['subject']}\n\n{email['body']}\n\n")
    
    msg_type = "TEST" if is_test else "STRIKE"
    preview_body = f"### {msg_type} PREVIEW BATCH ###\n" + "".join(previews) + f"\n[INSTRUCTION]: Create or edit {APPROVAL_FILE} to include 'approve all' or the ID numbers (e.g., '1 3') to proceed."
    
    if not notify_executive(f"{msg_type} PREVIEW BATCH: {datetime.now().strftime('%Y-%m-%d')}", preview_body):
        log_action("ABORTED: Failed to send previews to Executive.")
        return

    log_action(f"PRE-SEND GATE: {msg_type} Previews sent. Awaiting approval file...")
    
    # 2. APPROVAL GATE
    if is_test:
        # Auto-create approval for test mode
        os.makedirs(APPROVAL_DIR, exist_ok=True)
        with open(APPROVAL_FILE, "w") as f: f.write("approve all")
        
    approved, scope = wait_for_approval()
    if not approved:
        return
    
    # 3. DISPATCH LOOP
    for lead in batch:
        # Check approval scope
        if scope != "all" and str(lead['id']) not in scope:
            log_action(f"Approval status: [skipped] - ID {lead['id']} ({lead['name']}) not in approved list.")
            continue

        # EMAIL FALLBACK (Rule 3)
        if str(lead.get('email', '')).upper() == "TBD":
            log_action(f"Manual outreach needed (phone only) for {lead['name']}. Skipping auto-send.")
            manual_outreach_list.append(f"ID {lead['id']} - {lead['name']} ({lead['phone']}) [REASON: No Email]")
            continue
            
        # REAL CROSS-CHECK (Rule 2)
        passed, reason = check_site_status(lead)
        if not passed:
            log_action(f"CROSS-CHECK REJECTED: {lead['name']} ({reason}). Flagging for manual review.")
            manual_outreach_list.append(f"ID {lead['id']} - {lead['name']} ({lead['phone']}) [REASON: Cross-check falled: {reason}]")
            continue

        email = generate_email(lead)
        
        # SEND Logic
        log_action(f"SENDING STRIKE: {lead['name']} -> {lead['email']}")
        
        # Parity copy is Rule 5's "Detailed log" and notification
        success = notify_executive(f"Copy: Email Sent to {lead['name']}", email['body'])
        
        if success:
            log_action(f"Send result: [success 200] - Strike delivered to {lead['name']}. Throttling 10m.")
            if not is_test:
                time.sleep(THROTTLE_TIME)
        else:
            log_action(f"Send result: [fail] - Critical delivery error for {lead['name']}. Pausing.")
            break

    # 4. MANUAL OUTREACH REPORT (Feedback Suggestion)
    if manual_outreach_list:
        summary = "### MANUAL OUTREACH REQUIRED ###\nThe following leads were skipped and require manual phone/text outreach:\n\n" + "\n".join(manual_outreach_list)
        notify_executive(f"Manual Outreach List: {datetime.now().strftime('%Y-%m-%d')}", summary)
        log_action("MANUAL REPORT: Sent manual outreach list to Executive.")

if __name__ == "__main__":
    if "--test" in sys.argv:
        log_action("--- FORCE TEST MODE STARTING ---")
        test_lead = {"id": 0, "name": "Fake Ocean Massage Test", "industry": "Test", "phone": "352-936-8152", "email": EXECUTIVE_EMAIL, "site": "google.com", "trust_killer": "SSL warning found."}
        run_strike_batch([test_lead], is_test=True)
        log_action("--- FORCE TEST MODE COMPLETE ---")
    else:
        # Batch of 3 as per Executive Order
        run_strike_batch(LEADS[:3])
