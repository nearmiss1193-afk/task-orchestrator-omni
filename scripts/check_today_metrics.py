import os
import datetime
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(".env.local")

def get_supabase():
    url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
    return create_client(url, key)

def check_metrics():
    sb = get_supabase()
    
    # Get today's date in ISO format (start of day)
    today = datetime.date.today().isoformat()
    start_of_day = f"{today}T00:00:00"

    print(f"📊 Outreach Report for {today}")
    print("-" * 30)

    # 1. Emails & SMS (outbound_touches)
    # Assuming 'channel' column exists, or we count all touches
    try:
        touches = sb.table("outbound_touches")\
            .select("*", count="exact")\
            .gte("created_at", start_of_day)\
            .execute()
        
        email_count = 0
        sms_count = 0
        other_count = 0
        
        for t in touches.data:
            ch = t.get('channel', 'unknown').lower()
            if 'email' in ch:
                email_count += 1
            elif 'sms' in ch:
                sms_count += 1
            else:
                other_count += 1
                
        print(f"📧 Emails Sent: {email_count}")
        print(f"📱 SMS Sent:   {sms_count}")
        print(f"Other Touches: {other_count}")
        print(f"Total Touches: {touches.count}")

    except Exception as e:
        print(f"❌ Error checking touches: {e}")

    # 2. Calls (call_logs or similar)
    try:
        calls = sb.table("call_transcripts")\
            .select("*", count="exact")\
            .gte("created_at", start_of_day)\
            .execute()
        print(f"📞 Calls Made:  {calls.count}")
    except Exception as e:
        print(f"❌ Error checking calls: {e}")

if __name__ == "__main__":
    check_metrics()
