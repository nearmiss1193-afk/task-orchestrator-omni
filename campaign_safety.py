"""
CAMPAIGN SAFETY GATE - Throttle rules to prevent burning leads
"""
from datetime import datetime, timedelta
import requests

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# ============================================================================
# SAFETY RULES - Lead must pass ALL to receive outreach
# ============================================================================

BLOCKED_STATUSES = ["unsubscribed", "won", "booked", "opted_out", "do_not_contact"]
BLOCKED_SENTIMENTS = ["frustrated"]
MIN_HOURS_BETWEEN_OUTBOUND = 12
MIN_CONFIDENCE_TO_MESSAGE = 0.8


def can_message_lead(lead: dict) -> tuple:
    """
    Check if a lead can be messaged. Returns (can_message, reason)
    """
    phone = lead.get("phone")
    status = (lead.get("status") or "").lower()
    disposition = (lead.get("disposition") or "").lower()
    sentiment = (lead.get("sentiment") or "").lower()
    confidence = lead.get("confidence", 1.0)
    last_outbound = lead.get("last_outbound_at")
    
    # Rule 1: Check blocked statuses
    if status in BLOCKED_STATUSES or disposition in BLOCKED_STATUSES:
        return False, f"Blocked status: {status or disposition}"
    
    # Rule 2: Check sentiment (escalate instead)
    if sentiment in BLOCKED_SENTIMENTS:
        return False, f"Blocked sentiment: {sentiment} - requires escalation"
    
    # Rule 3: Check confidence threshold
    if confidence < MIN_CONFIDENCE_TO_MESSAGE:
        return False, f"Low confidence ({confidence}) - needs human review"
    
    # Rule 4: Check timing (12 hours between messages)
    if last_outbound:
        try:
            last_time = datetime.fromisoformat(last_outbound.replace("Z", "+00:00"))
            hours_since = (datetime.now(last_time.tzinfo) - last_time).total_seconds() / 3600
            if hours_since < MIN_HOURS_BETWEEN_OUTBOUND:
                return False, f"Too soon - {hours_since:.1f}h since last outbound (min: {MIN_HOURS_BETWEEN_OUTBOUND}h)"
        except:
            pass
    
    return True, "OK"


def get_safe_leads(limit: int = 10) -> list:
    """
    Get leads that are safe to message (pass all safety rules)
    """
    # Get new leads
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=HEADERS,
        params={"status": "eq.new", "limit": limit * 3}  # Get more to filter
    )
    
    if r.status_code != 200:
        return []
    
    leads = r.json()
    safe_leads = []
    
    for lead in leads:
        can_msg, reason = can_message_lead(lead)
        if can_msg:
            safe_leads.append(lead)
            if len(safe_leads) >= limit:
                break
        else:
            print(f"[BLOCKED] {lead.get('company_name', 'Unknown')}: {reason}")
    
    return safe_leads


def update_last_outbound(lead_id: str):
    """Mark lead as just messaged"""
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead_id}",
        headers=HEADERS,
        json={"last_outbound_at": datetime.utcnow().isoformat() + "Z"}
    )


# ============================================================================
# DISPOSITION ENFORCEMENT - Every interaction MUST end with disposition
# ============================================================================

VALID_DISPOSITIONS = [
    "booked",           # Appointment scheduled
    "sent_link",        # Booking link sent, awaiting action
    "follow_up_scheduled",  # Follow-up planned
    "not_fit",          # Disqualified
    "escalated",        # Sent to human
    "opted_out",        # User requested STOP
    "no_response",      # Outbound with no reply yet
    "engaged",          # Replied but not booked
]


def set_disposition(phone: str, disposition: str) -> bool:
    """
    Set disposition for a contact. REQUIRED after every interaction.
    """
    if disposition not in VALID_DISPOSITIONS:
        print(f"[ERROR] Invalid disposition: {disposition}")
        return False
    
    # Update contact
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/contacts?phone=eq.{phone}",
        headers=HEADERS,
        json={
            "disposition": disposition,
            "disposition_at": datetime.utcnow().isoformat() + "Z"
        }
    )
    
    # Also update lead if exists
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/leads?phone=eq.{phone}",
        headers=HEADERS,
        json={"disposition": disposition}
    )
    
    return r.status_code in [200, 204]


def check_missing_dispositions() -> list:
    """Find contacts with interactions but no disposition"""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/contacts",
        headers=HEADERS,
        params={
            "disposition": "is.null",
            "interaction_count": "gt.0",
            "limit": 50
        }
    )
    return r.json() if r.status_code == 200 else []


# ============================================================================
# LEAD SEGMENTATION - Hot/Warm/Cold/Not Fit/DNC
# ============================================================================

def segment_lead(lead: dict) -> str:
    """
    Classify lead into segment based on behavior
    """
    status = (lead.get("status") or "").lower()
    disposition = (lead.get("disposition") or "").lower()
    sentiment = (lead.get("sentiment") or "").lower()
    intent = (lead.get("intent") or "").lower()
    interaction_count = lead.get("interaction_count", 0)
    
    # Do Not Contact
    if status in ["unsubscribed", "opted_out"] or disposition == "opted_out":
        return "do_not_contact"
    
    # Not Fit
    if disposition == "not_fit" or "solo" in str(lead.get("notes", "")).lower():
        return "not_fit"
    
    # Hot: replied, asked pricing, asked booking
    if intent in ["pricing", "book", "interest"] or disposition in ["engaged", "sent_link"]:
        return "hot"
    
    # Warm: opened/engaged then silent, or some interaction
    if interaction_count > 0 and disposition not in ["booked", "not_fit", "opted_out"]:
        return "warm"
    
    # Cold: no engagement
    return "cold"


def segment_all_leads():
    """Segment all leads in database"""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/leads",
        headers=HEADERS,
        params={"limit": 200}
    )
    
    if r.status_code != 200:
        return {}
    
    leads = r.json()
    segments = {"hot": 0, "warm": 0, "cold": 0, "not_fit": 0, "do_not_contact": 0}
    
    for lead in leads:
        segment = segment_lead(lead)
        segments[segment] += 1
        
        # Update lead with segment
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/leads?id=eq.{lead['id']}",
            headers=HEADERS,
            json={"segment": segment}
        )
    
    return segments


# ============================================================================
# TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CAMPAIGN SAFETY GATE - TEST")
    print("=" * 60)
    
    # Test get safe leads
    safe = get_safe_leads(5)
    print(f"\n[SAFE LEADS] {len(safe)} leads ready for outreach")
    
    # Test segmentation
    print("\n[SEGMENTING LEADS]")
    segments = segment_all_leads()
    print(f"Results: {segments}")
    
    # Check missing dispositions
    missing = check_missing_dispositions()
    print(f"\n[MISSING DISPOSITIONS] {len(missing)} contacts need disposition")
