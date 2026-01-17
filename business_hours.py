"""
BUSINESS HOURS SCHEDULER - Send outreach only during lead's local business hours
Respects timezone and schedules for next business day if outside 8:00-17:00
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json

# US Timezone mappings by state/area code
TIMEZONE_MAP = {
    # Eastern (ET)
    "FL": "America/New_York", "GA": "America/New_York", "NC": "America/New_York",
    "SC": "America/New_York", "VA": "America/New_York", "NY": "America/New_York",
    "NJ": "America/New_York", "PA": "America/New_York", "OH": "America/New_York",
    "MI": "America/New_York", "MA": "America/New_York", "CT": "America/New_York",
    # Central (CT)
    "TX": "America/Chicago", "IL": "America/Chicago", "MO": "America/Chicago",
    "TN": "America/Chicago", "AL": "America/Chicago", "LA": "America/Chicago",
    "MN": "America/Chicago", "WI": "America/Chicago", "IA": "America/Chicago",
    # Mountain (MT)
    "CO": "America/Denver", "AZ": "America/Phoenix", "UT": "America/Denver",
    "NM": "America/Denver", "MT": "America/Denver", "ID": "America/Denver",
    # Pacific (PT)
    "CA": "America/Los_Angeles", "WA": "America/Los_Angeles", "OR": "America/Los_Angeles",
    "NV": "America/Los_Angeles",
}

# Area code to timezone (common ones)
AREA_CODE_TZ = {
    # Florida (Eastern)
    "305": "America/New_York", "786": "America/New_York", "954": "America/New_York",
    "561": "America/New_York", "407": "America/New_York", "321": "America/New_York",
    "813": "America/New_York", "727": "America/New_York", "352": "America/New_York",
    "863": "America/New_York", "239": "America/New_York", "941": "America/New_York",
    # Texas (Central)
    "214": "America/Chicago", "972": "America/Chicago", "469": "America/Chicago",
    "713": "America/Chicago", "832": "America/Chicago", "281": "America/Chicago",
    "210": "America/Chicago", "512": "America/Chicago", "817": "America/Chicago",
    # California (Pacific)
    "213": "America/Los_Angeles", "310": "America/Los_Angeles", "323": "America/Los_Angeles",
    "818": "America/Los_Angeles", "415": "America/Los_Angeles", "408": "America/Los_Angeles",
    "619": "America/Los_Angeles", "858": "America/Los_Angeles", "714": "America/Los_Angeles",
    # New York (Eastern)
    "212": "America/New_York", "718": "America/New_York", "917": "America/New_York",
    "516": "America/New_York", "914": "America/New_York", "631": "America/New_York",
}

# Business hours
BUSINESS_START = 8   # 8:00 AM
BUSINESS_END = 17    # 5:00 PM


def get_lead_timezone(lead: dict) -> str:
    """Determine lead's timezone from state or phone area code"""
    # Try state first
    state = (lead.get("state") or "").upper()
    if state in TIMEZONE_MAP:
        return TIMEZONE_MAP[state]
    
    # Try phone area code
    phone = lead.get("phone", "")
    phone_clean = phone.replace("+1", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    if len(phone_clean) >= 10:
        area_code = phone_clean[:3]
        if area_code in AREA_CODE_TZ:
            return AREA_CODE_TZ[area_code]
    
    # Default to Eastern
    return "America/New_York"


def is_business_hours(lead: dict, utc_now: datetime = None) -> bool:
    """Check if current UTC time is within lead's local business hours"""
    if utc_now is None:
        utc_now = datetime.now(ZoneInfo("UTC"))
    
    tz_name = get_lead_timezone(lead)
    local_tz = ZoneInfo(tz_name)
    local_now = utc_now.astimezone(local_tz)
    
    # Check weekday (Mon=0, Sun=6)
    if local_now.weekday() >= 5:  # Weekend
        return False
    
    # Check hours
    if local_now.hour < BUSINESS_START or local_now.hour >= BUSINESS_END:
        return False
    
    return True


def get_next_send_time(lead: dict, utc_now: datetime = None) -> datetime:
    """Get next valid send time in lead's local business hours"""
    if utc_now is None:
        utc_now = datetime.now(ZoneInfo("UTC"))
    
    tz_name = get_lead_timezone(lead)
    local_tz = ZoneInfo(tz_name)
    local_now = utc_now.astimezone(local_tz)
    
    # Start with current time
    next_send = local_now
    
    # If after business hours today, move to next day
    if next_send.hour >= BUSINESS_END:
        next_send = next_send.replace(hour=BUSINESS_START, minute=0, second=0)
        next_send += timedelta(days=1)
    
    # If before business hours, set to start
    if next_send.hour < BUSINESS_START:
        next_send = next_send.replace(hour=BUSINESS_START, minute=0, second=0)
    
    # Skip weekends
    while next_send.weekday() >= 5:
        next_send += timedelta(days=1)
    
    # Convert back to UTC
    return next_send.astimezone(ZoneInfo("UTC"))


def should_send_now(lead: dict) -> tuple:
    """
    Check if we should send to this lead now.
    Returns (can_send: bool, next_send_time: datetime, reason: str)
    """
    if is_business_hours(lead):
        return True, None, "Within business hours"
    else:
        next_time = get_next_send_time(lead)
        tz_name = get_lead_timezone(lead)
        return False, next_time, f"Outside business hours ({tz_name})"


def schedule_for_business_hours(leads: list) -> dict:
    """Categorize leads by send eligibility"""
    result = {
        "send_now": [],
        "schedule_later": []
    }
    
    for lead in leads:
        can_send, next_time, reason = should_send_now(lead)
        
        if can_send:
            result["send_now"].append(lead)
        else:
            result["schedule_later"].append({
                "lead": lead,
                "next_send_utc": next_time.isoformat() if next_time else None,
                "reason": reason
            })
    
    return result


# Test
if __name__ == "__main__":
    print("Business Hours Scheduler Test")
    print("=" * 50)
    
    test_leads = [
        {"name": "FL Lead", "phone": "+18635551234", "state": "FL"},
        {"name": "TX Lead", "phone": "+12145551234", "state": "TX"},
        {"name": "CA Lead", "phone": "+13105551234", "state": "CA"},
    ]
    
    for lead in test_leads:
        can_send, next_time, reason = should_send_now(lead)
        tz = get_lead_timezone(lead)
        print(f"{lead['name']} ({tz}): {'SEND NOW' if can_send else f'SCHEDULE: {next_time}'} - {reason}")
