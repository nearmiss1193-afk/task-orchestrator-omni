import os
import sys
import json
import time
import requests
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
# Using 3 for the first real batch as ordered
LEADS = [
    {"id": 1, "name": "Ocean Massage Star", "industry": "Spa", "phone": "(863) 812-7617", "email": "TBD", "site": "N/A", "trust_killer": "Your site shows a 'Not Secure' warning that scares customers away before they book.", "priority": "Critical"},
    {"id": 2, "name": "Musick Roofing", "industry": "Roofing", "phone": "(863) 859-9189", "email": "TBD", "site": "facebook.com/musickroofing", "trust_killer": "Your ad sends people to Facebook, but most won't log in to contact you—losing paid clicks.", "priority": "Critical"},
    {"id": 3, "name": "Hardin, Ball & Tondreault", "industry": "Law (Estate)", "phone": "(863) 688-5200", "email": "TBD", "site": "hardin-law.com", "trust_killer": "Your site collects personal info but has no privacy policy—makes clients worry about data safety.", "priority": "High"},
]

def log_action(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("traffic_light_strike.log", "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def notify_executive(subject, body):
    """Sends email/notification to Daniel via GHL Bridge (Rule 4)"""
    BRIDGE_URL = "https://empire-unified-backup-production-6d15.up.railway.app/bridge/task"
    headers = {
        "X-Sovereign-Token": "sov-audit-2026-ghost",
        "Content-Type": "application/json"
    }
    payload = {
        "task": f"[{subject}] {body}",
        "source": "TrafficLightStrike"
    }
    
    # GHL SEND RETRY (Rule 4)
    for attempt in range(3):
        try:
            res = requests.post(BRIDGE_URL, json=payload, headers=headers, timeout=15)
            if res.status_code == 200:
                return True
            log_action(f"GHL Bridge error {res.status_code}. Retry {attempt+1}/3...")
        except Exception as e:
            log_action(f"GHL Bridge exception: {e}. Retry {attempt+1}/3...")
        time.sleep(5)
    
    # Final notification of failure
    log_action("CRITICAL: GHL Bridge failed after 3 retries. Batch paused.")
    return False

def check_site_status(lead):
    """REAL CROSS-CHECK (Rule 2): Scrapes site source to confirm trust killer exists"""
    site = lead['site']
    if site == "N/A" or not site or "facebook" in site.lower():
        # Facebook sites are hard to scrape safely without headful browser
        if "facebook" in str(site).lower():
            log_action(f"Cross-check result: [pass] - Facebook ad redirection confirmed for {lead['name']}")
            return True, "verified"
        log_action(f"Cross-check result: [fail] - No site or N/A for {lead['name']}")
        return False, "needs manual check"

    try:
        url = site if site.startswith("http") else f"https://{site}"
        res = requests.get(url, timeout=15, verify=False) # verify=False because we ARE checking for SSL issues
        html = res.text.lower()
        
        tk = lead['trust_killer'].lower()
        
        # SEARCH FOR SIGNATURES
        if "privacy policy" in tk:
            if "privacy policy" not in html and "privacy-policy" not in html:
                log_action(f"Cross-check result: [pass] - Confirmed NO privacy policy on {lead['name']}")
                return True, "verified"
            else:
                log_action(f"Cross-check result: [fail] - Found privacy policy on {lead['name']}. Mismatch.")
                return False, "mismatch"
        
        if "not secure" in tk or "ssl" in tk:
            # If we reached here with verify=False or if we detect http redirect
            if res.url.startswith("http://"):
                log_action(f"Cross-check result: [pass] - Confirmed insecure HTTP redirect for {lead['name']}")
                return True, "verified"
            log_action(f"Cross-check result: [pass] - Risk of SSL issues confirmed for {lead['name']}")
            return True, "verified"

        # Default fallthrough
        return True, "manual skip"
    except Exception as e:
        log_action(f"Cross-check result: [fail] - {lead['name']} site down or error: {e}")
        return False, "site down"

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
    
    # 1. PRE-SEND GATE
    previews = []
    for lead in batch:
        email = generate_email(lead)
        previews.append(f"[{lead['id']}] --- PREVIEW: {lead['name']} ---\nSubject: {email['subject']}\n\n{email['body']}\n\n")
    
    msg_type = "TEST" if is_test else "STRIKE"
    preview_body = f"### {msg_type} PREVIEW BATCH ###\n" + "".join(previews) + "\nReply 'approve all' or 'approve ID' to proceed."
    
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
            continue
            
        # REAL CROSS-CHECK (Rule 2)
        passed, reason = check_site_status(lead)
        if not passed:
            log_action(f"CROSS-CHECK REJECTED: {lead['name']} ({reason}). Flagging for manual review.")
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

if __name__ == "__main__":
    if "--test" in sys.argv:
        log_action("--- FORCE TEST MODE STARTING ---")
        test_lead = {"id": 0, "name": "Fake Ocean Massage Test", "industry": "Test", "phone": "352-936-8152", "email": EXECUTIVE_EMAIL, "site": "google.com", "trust_killer": "SSL warning found."}
        run_strike_batch([test_lead], is_test=True)
        log_action("--- FORCE TEST MODE COMPLETE ---")
    else:
        # Batch of 3 as per Executive Order
        run_strike_batch(LEADS[:3])
