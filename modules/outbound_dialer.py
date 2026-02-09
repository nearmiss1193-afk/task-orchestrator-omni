"""
VAPI OUTBOUND DIALER
====================
Makes outbound sales calls to prospects using Sarah AI.

Usage:
    from modules.outbound_dialer import dial_prospect, dial_batch
    
    # Single call
    dial_prospect("+1234567890", "Cool Breeze HVAC", "Tampa")
    
    # Batch from leads
    dial_batch(count=10)
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Vapi configuration
VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID") or "86f73243-8916-4897-b840-b20c8afdd7a8339f"

# Your Vapi assistant IDs
SARAH_ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a"  # Sarah 3.0 (Official)
JOHN_ASSISTANT_ID = "ce4d14a2-2c7e-4eb5-b2d8-ca84ad5e2c3b"   # John Office Manager

VAPI_API_URL = "https://api.vapi.ai/call"


def dial_prospect(phone_number: str, company_name: str = "", city: str = "", 
                  assistant_id: str = None, first_message: str = None,
                  metadata_overrides: dict = None) -> dict:
    """
    Make an outbound call to a prospect with Metadata Injection support.
    
    Args:
        phone_number: Customer phone number (E.164 format: +1XXXXXXXXXX)
        company_name: Company name for context
        city: City for context
        assistant_id: Which assistant to use (defaults to Sarah)
        metadata_overrides: Context metadata for Sarah's memory (Phase 5)
    """
    if not VAPI_PRIVATE_KEY:
        return {"error": "VAPI_PRIVATE_KEY not configured"}
    
    if not VAPI_PHONE_NUMBER_ID:
        return {"error": "VAPI_PHONE_NUMBER_ID not configured"}
    
    # Clean phone number
    if not phone_number.startswith("+"):
        phone_number = "+1" + phone_number.replace("-", "").replace(" ", "")
    
    # Build payload - MUST include type for outbound calls
    payload = {
        "type": "outboundPhoneCall",
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "assistantId": assistant_id or SARAH_ASSISTANT_ID,
        "customer": {
            "number": phone_number,
            "name": company_name or "Prospect",
        }
    }
    
    # Optional: Add context as metadata
    if company_name or city or metadata_overrides:
        payload["metadata"] = {
            "company_name": company_name,
            "city": city,
            "source": "outbound_dialer",
            "timestamp": datetime.now().isoformat()
        }
        if metadata_overrides:
            from modules.vapi.metadata_injector import inject_metadata_into_payload
            payload = inject_metadata_into_payload(payload, metadata_overrides)
    
    try:
        response = requests.post(
            VAPI_API_URL,
            headers={
                "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"[DIALER] ✅ Call initiated to {phone_number}")
            print(f"         Call ID: {result.get('id', 'unknown')}")
            return {
                "success": True,
                "call_id": result.get("id"),
                "phone": phone_number,
                "company": company_name,
                "status": "initiated"
            }
        else:
            print(f"[DIALER] ❌ Failed: {response.status_code} - {response.text}")
            return {
                "success": False,
                "error": response.text,
                "status_code": response.status_code
            }
            
    except Exception as e:
        print(f"[DIALER] ❌ Exception: {e}")
        return {"success": False, "error": str(e)}


def dial_batch(count: int = 5, status_filter: str = "contacted") -> list:
    """
    Dial multiple prospects from the leads database.
    
    Args:
        count: How many to call
        status_filter: Which lead status to target
    
    Returns:
        List of call results
    """
    from supabase import create_client
    
    supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supa_url or not supa_key:
        return [{"error": "Supabase not configured"}]
    
    client = create_client(supa_url, supa_key)
    
    # Get leads to call
    result = client.table("leads").select("*")\
        .eq("status", status_filter)\
        .limit(count)\
        .execute()
    
    leads = result.data
    print(f"[DIALER] Found {len(leads)} leads with status '{status_filter}'")
    
    results = []
    for lead in leads:
        # Get phone from agent_research or direct field
        meta = lead.get("agent_research", {})
        if isinstance(meta, str):
            import json
            try:
                meta = json.loads(meta)
            except:
                meta = {}
        
        phone = meta.get("phone") or lead.get("phone") or lead.get("phone_number")
        company = lead.get("company_name") or "Prospect"
        city = meta.get("city") or ""
        
        if phone:
            print(f"\n[DIALER] Calling: {company} at {phone}")
            call_result = dial_prospect(phone, company, city)
            results.append(call_result)
            
            # Update lead status
            if call_result.get("success"):
                client.table("leads").update({
                    "status": "called",
                    "last_called": datetime.now().isoformat()
                }).eq("id", lead["id"]).execute()
        else:
            print(f"[DIALER] ⚠️ No phone for {company}")
            results.append({"error": "No phone number", "company": company})
    
    return results


def schedule_calls(hour: int = 10, minute: int = 0, count: int = 10):
    """
    Schedule outbound calls for a specific time.
    Saves schedule to Supabase for the Modal scheduler to execute.
    """
    from supabase import create_client
    from datetime import datetime, timedelta
    
    supa_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supa_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supa_url or not supa_key:
        return {"error": "Supabase not configured"}
    
    client = create_client(supa_url, supa_key)
    
    # Calculate next run time
    now = datetime.now()
    scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if scheduled_time <= now:
        scheduled_time += timedelta(days=1)
    
    # Save schedule
    client.table("system_logs").insert({
        "level": "INFO",
        "event_type": "OUTBOUND_SCHEDULE",
        "message": f"Scheduled {count} outbound calls for {scheduled_time.isoformat()}",
        "metadata": {
            "scheduled_time": scheduled_time.isoformat(),
            "count": count,
            "status": "pending"
        }
    }).execute()
    
    print(f"[SCHEDULER] Scheduled {count} calls for {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
    return {"scheduled": True, "time": scheduled_time.isoformat(), "count": count}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Vapi Outbound Dialer")
    parser.add_argument("--phone", help="Phone number to call")
    parser.add_argument("--company", default="", help="Company name")
    parser.add_argument("--batch", type=int, help="Call N leads from database")
    parser.add_argument("--test", action="store_true", help="Test call to your number")
    
    args = parser.parse_args()
    
    if args.test:
        test_phone = os.getenv("TEST_PHONE", "+13529368152")
        print(f"[TEST] Calling your number: {test_phone}")
        result = dial_prospect(test_phone, "Test Company", "Test City")
        print(result)
    elif args.phone:
        result = dial_prospect(args.phone, args.company)
        print(result)
    elif args.batch:
        results = dial_batch(count=args.batch)
        print(f"\nCompleted {len(results)} dial attempts")
    else:
        print("Usage:")
        print("  python outbound_dialer.py --test")
        print("  python outbound_dialer.py --phone +15551234567 --company 'ABC HVAC'")
        print("  python outbound_dialer.py --batch 5")
