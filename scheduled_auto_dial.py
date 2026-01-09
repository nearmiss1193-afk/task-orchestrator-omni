"""
SCHEDULED AUTO-DIALER
=====================
Automatically calls leads at scheduled times.
Runs as part of Modal scheduler or standalone.

Usage:
    python scheduled_auto_dial.py --now        # Dial immediately
    python scheduled_auto_dial.py --schedule   # Set up schedule for 10 AM
"""
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Config
DIAL_BATCH_SIZE = 5  # Calls per batch
DIAL_INTERVAL_MINUTES = 3  # Minutes between calls (avoid spam)
DIAL_HOURS = [10, 14]  # Default dial hours (10 AM, 2 PM)


def get_clients():
    """Get Supabase client"""
    supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(supa_url, supa_key) if supa_url and supa_key else None


def get_leads_to_call(count: int = 5) -> list:
    """Get leads that are ready to be called"""
    client = get_clients()
    if not client:
        return []
    
    # Get leads with status 'contacted' (emailed but not called)
    result = client.table("leads").select("*")\
        .eq("status", "contacted")\
        .order("created_at", desc=True)\
        .limit(count)\
        .execute()
    
    return result.data


def run_dial_batch():
    """Run a batch of outbound calls NOW"""
    from modules.outbound_dialer import dial_prospect
    
    print("="*60)
    print(f"AUTO-DIALER BATCH - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    leads = get_leads_to_call(DIAL_BATCH_SIZE)
    print(f"Found {len(leads)} leads to call")
    
    if not leads:
        print("No leads ready to call")
        return {"calls": 0, "success": 0}
    
    results = {"calls": 0, "success": 0, "failed": 0, "details": []}
    client = get_clients()
    
    for lead in leads:
        # Extract phone
        meta = lead.get("agent_research", {})
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except:
                meta = {}
        
        phone = meta.get("phone") or lead.get("phone")
        company = lead.get("company_name", "Prospect")
        city = meta.get("city", "")
        
        if not phone:
            print(f"  ⚠️ No phone for {company}")
            continue
        
        print(f"\n  📞 Calling: {company} at {phone}")
        results["calls"] += 1
        
        # Make call
        call_result = dial_prospect(phone, company, city)
        
        if call_result.get("success"):
            results["success"] += 1
            results["details"].append({"company": company, "phone": phone, "status": "success"})
            
            # Update lead status
            if client:
                client.table("leads").update({
                    "status": "called",
                    "last_called": datetime.now().isoformat()
                }).eq("id", lead["id"]).execute()
        else:
            results["failed"] += 1
            results["details"].append({"company": company, "phone": phone, "status": "failed", "error": call_result.get("error")})
    
    # Log results
    if client:
        client.table("system_logs").insert({
            "level": "INFO",
            "event_type": "AUTO_DIAL_BATCH",
            "message": f"Called {results['success']}/{results['calls']} leads",
            "metadata": results
        }).execute()
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {results['success']}/{results['calls']} successful")
    print("="*60)
    
    return results


def schedule_next_dial():
    """Schedule the next dial batch"""
    client = get_clients()
    if not client:
        return {"error": "No database connection"}
    
    now = datetime.now()
    
    # Find next dial time
    for hour in DIAL_HOURS:
        next_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if next_time > now:
            break
    else:
        # Tomorrow at first hour
        next_time = (now + timedelta(days=1)).replace(hour=DIAL_HOURS[0], minute=0, second=0, microsecond=0)
    
    # Save schedule
    client.table("system_logs").insert({
        "level": "INFO",
        "event_type": "DIAL_SCHEDULED",
        "message": f"Next auto-dial batch at {next_time.strftime('%Y-%m-%d %H:%M')}",
        "metadata": {"scheduled_time": next_time.isoformat(), "batch_size": DIAL_BATCH_SIZE}
    }).execute()
    
    print(f"[SCHEDULER] Next dial batch: {next_time.strftime('%Y-%m-%d %H:%M')}")
    return {"scheduled": next_time.isoformat()}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scheduled Auto-Dialer")
    parser.add_argument("--now", action="store_true", help="Run dial batch now")
    parser.add_argument("--schedule", action="store_true", help="Schedule next batch")
    parser.add_argument("--count", type=int, default=5, help="Number of leads to call")
    
    args = parser.parse_args()
    
    if args.now:
        DIAL_BATCH_SIZE = args.count
        run_dial_batch()
    elif args.schedule:
        schedule_next_dial()
    else:
        print("Usage:")
        print("  python scheduled_auto_dial.py --now           # Dial leads now")
        print("  python scheduled_auto_dial.py --schedule      # Schedule for later")
        print("  python scheduled_auto_dial.py --now --count 3 # Dial 3 leads")
