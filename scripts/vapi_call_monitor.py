"""
Vapi Call Monitor - Bypass for broken webhooks.
Polls Vapi API for completed calls and notifies Dan via GHL webhook.
This runs as a Modal CRON job every 2 minutes.
"""
import os, json, requests, time
from datetime import datetime, timezone, timedelta

def check_and_notify():
    """Poll Vapi for recent completed calls and notify Dan"""
    vapi_key = os.environ.get('VAPI_PRIVATE_KEY')
    
    if not vapi_key:
        print("ERROR: No VAPI_PRIVATE_KEY")
        return {"error": "no key"}
    
    headers = {'Authorization': f'Bearer {vapi_key}'}
    
    # Get recent calls (last 5 minutes)
    try:
        r = requests.get('https://api.vapi.ai/call?limit=5', headers=headers, timeout=15)
        calls = r.json()
    except Exception as e:
        print(f"Vapi API error: {e}")
        return {"error": str(e)}
    
    # Track which calls we've already notified about
    # Use Supabase to store processed call IDs
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')
    
    sb_headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    dan_phone = "+13529368152"
    ghl_webhook = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd"
    
    notified = 0
    
    for call in calls:
        call_id = call.get('id', '')
        status = call.get('status', '')
        ended_at = call.get('endedAt')
        
        # Only process completed calls
        if status != 'ended' or not ended_at:
            continue
        
        # Only process calls from the last 10 minutes
        try:
            end_time = datetime.fromisoformat(ended_at.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            age = (now - end_time).total_seconds()
            if age > 600:  # Older than 10 min, skip
                continue
        except:
            continue
        
        # Check if already notified (using vapi_call_logs table or simple file)
        # For now, use Supabase to check
        try:
            check = requests.get(
                f"{supabase_url}/rest/v1/vapi_call_notifications?call_id=eq.{call_id}&select=call_id",
                headers=sb_headers, timeout=5
            )
            if check.status_code == 200 and check.json():
                continue  # Already notified
        except:
            pass  # If table doesn't exist, proceed anyway
        
        # Extract call details
        customer = call.get('customer', {}).get('number', 'Unknown')
        messages = call.get('messages', [])
        msg_count = len(messages) if messages else 0
        
        # Get last few messages for summary
        summary_parts = []
        if messages:
            for m in messages[-3:]:
                role = m.get('role', '?')
                text = str(m.get('message', ''))[:80]
                if text:
                    summary_parts.append(f"{role}: {text}")
        
        # Calculate duration
        created_at = call.get('createdAt', '')
        duration_str = "unknown"
        try:
            start = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            end = datetime.fromisoformat(ended_at.replace('Z', '+00:00'))
            seconds = int((end - start).total_seconds())
            duration_str = f"{seconds // 60}m {seconds % 60}s"
        except:
            pass
        
        # Build notification message
        notify_msg = (
            f"Sarah AI Call Report\n"
            f"Caller: {customer}\n"
            f"Duration: {duration_str}\n"
            f"Messages: {msg_count}\n"
        )
        if summary_parts:
            notify_msg += f"\nLast exchange:\n" + "\n".join(summary_parts[-2:])
        
        # Send notification via GHL
        try:
            payload = {"phone": dan_phone, "message": notify_msg}
            r2 = requests.post(ghl_webhook, json=payload, timeout=10)
            print(f"Notified Dan about call {call_id}: {r2.status_code}")
            notified += 1
            
            # Mark as notified in Supabase
            try:
                requests.post(
                    f"{supabase_url}/rest/v1/vapi_call_notifications",
                    headers=sb_headers,
                    json={"call_id": call_id, "customer_phone": customer, "notified_at": datetime.now(timezone.utc).isoformat()},
                    timeout=5
                )
            except:
                pass  # Table may not exist yet, that's ok
                
        except Exception as e:
            print(f"Failed to notify about call {call_id}: {e}")
    
    print(f"Processed {len(calls)} calls, notified {notified} new")
    return {"calls_checked": len(calls), "notified": notified}


if __name__ == '__main__':
    # Test locally
    from dotenv import load_dotenv
    load_dotenv()
    load_dotenv('.env.local')
    result = check_and_notify()
    print(json.dumps(result, indent=2))
