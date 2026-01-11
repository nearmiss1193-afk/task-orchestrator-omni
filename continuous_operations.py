"""
24/7 Continuous Operations Manager
Orchestrates all activities based on time of day and timezone
"""

import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

def get_current_time_est():
    """Get current time in EST"""
    return datetime.now(ZoneInfo("America/New_York"))

def get_current_time_pst():
    """Get current time in PST"""
    return datetime.now(ZoneInfo("America/Los_Angeles"))

def get_current_time_hst():
    """Get current time in HST (Hawaii)"""
    return datetime.now(ZoneInfo("Pacific/Honolulu"))

def is_business_hours_pst():
    """Check if it's business hours (9 AM - 8 PM) in PST"""
    pst_time = get_current_time_pst()
    hour = pst_time.hour
    return 9 <= hour < 20  # 9 AM to 8 PM

def is_business_hours_hst():
    """Check if it's business hours (9 AM - 8 PM) in HST"""
    hst_time = get_current_time_hst()
    hour = hst_time.hour
    return 9 <= hour < 20

def should_call_west_coast():
    """Determine if we should be calling CA/OR/WA"""
    return is_business_hours_pst()

def should_call_hawaii():
    """Determine if we should be calling Hawaii"""
    return is_business_hours_hst()

def get_current_activity():
    """
    Determine what activity should be happening right now
    Returns: dict with activity type and details
    """
    est_time = get_current_time_est()
    hour_est = est_time.hour
    
    # Check if we can call/SMS any region
    can_call_west = should_call_west_coast()
    can_call_hi = should_call_hawaii()
    
    if can_call_west or can_call_hi:
        # Business hours - calling and SMS
        regions = []
        if can_call_west:
            regions.extend(["CA", "OR", "WA"])
        if can_call_hi:
            regions.append("HI")
        
        return {
            "activity": "OUTREACH",
            "type": "calling_sms",
            "regions": regions,
            "priority": "high"
        }
    
    elif 1 <= hour_est < 8:
        # Late night/early morning - Decision maker research + system analysis
        return {
            "activity": "RESEARCH",
            "type": "decision_maker_research",
            "priority": "medium"
        }
    
    else:
        # Off-hours - Build prospect lists
        return {
            "activity": "PROSPECTING",
            "type": "build_prospect_lists",
            "regions": ["CA", "OR", "WA", "HI"],
            "priority": "low"
        }

def run_outreach_campaign(regions):
    """Run calling + SMS campaign for specified regions"""
    from ca_hi_blitz import main as run_campaign
    
    print(f"🚀 Starting outreach campaign for: {', '.join(regions)}")
    
    # Filter leads by region and run campaign
    # This would integrate with existing campaign scripts
    run_campaign()

def run_prospect_builder(regions):
    """Build prospect lists for specified regions"""
    from west_coast_prospector import build_prospects
    
    print(f"🔍 Building prospect lists for: {', '.join(regions)}")
    
    for region in regions:
        build_prospects(state=region, target_count=250)

def run_decision_maker_research():
    """Perform decision maker research on prospects without owner info"""
    print(f"📊 Running decision maker research...")
    
    # Get prospects without decision maker info
    # Run LinkedIn research
    # Update dossiers
    # This integrates with top_20_prospects workflow

def main():
    """Main 24/7 continuous operations loop"""
    print("="*70)
    print("24/7 CONTINUOUS OPERATIONS MANAGER")
    print("="*70)
    
    est_time = get_current_time_est()
    pst_time = get_current_time_pst()
    hst_time = get_current_time_hst()
    
    print(f"\nCurrent Time:")
    print(f"  EST: {est_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  PST: {pst_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  HST: {hst_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Determine current activity
    activity = get_current_activity()
    
    print(f"\nCurrent Activity: {activity['activity']}")
    print(f"Type: {activity['type']}")
    print(f"Priority: {activity['priority']}")
    
    if activity['activity'] == "OUTREACH":
        print(f"Regions: {', '.join(activity['regions'])}")
        run_outreach_campaign(activity['regions'])
    
    elif activity['activity'] == "PROSPECTING":
        print(f"Regions: {', '.join(activity['regions'])}")
        run_prospect_builder(activity['regions'])
    
    elif activity['activity'] == "RESEARCH":
        run_decision_maker_research()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
