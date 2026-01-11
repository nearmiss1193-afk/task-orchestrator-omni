"""
FETCH VAPI CALL TRANSCRIPTS AND UPDATE DASHBOARD
=================================================
Gets all call transcripts from today and stores them for dashboard display
"""
import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

VAPI_PRIVATE_KEY = os.getenv('VAPI_PRIVATE_KEY')
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_todays_calls():
    """Fetch all calls from today via Vapi API"""
    print("📞 Fetching today's calls from Vapi...")
    
    try:
        headers = {"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"}
        
        # Get calls from last 24 hours
        res = requests.get(
            "https://api.vapi.ai/call",
            headers=headers,
            params={"limit": 100},
            timeout=30
        )
        
        if res.status_code == 200:
            calls = res.json()
            today = datetime.now().date()
            
            today_calls = []
            for call in calls:
                call_date = call.get('createdAt', '')[:10]
                if call_date == str(today):
                    today_calls.append(call)
            
            print(f"Found {len(today_calls)} calls today")
            return today_calls
        else:
            print(f"Vapi API error: {res.status_code}")
            return []
            
    except Exception as e:
        print(f"Error fetching calls: {e}")
        return []

def get_call_transcript(call_id):
    """Get transcript for a specific call"""
    try:
        headers = {"Authorization": f"Bearer {VAPI_PRIVATE_KEY}"}
        res = requests.get(
            f"https://api.vapi.ai/call/{call_id}",
            headers=headers,
            timeout=30
        )
        
        if res.status_code == 200:
            call_data = res.json()
            return {
                'id': call_id,
                'customer_name': call_data.get('customer', {}).get('name', 'Unknown'),
                'customer_phone': call_data.get('customer', {}).get('number', ''),
                'status': call_data.get('status', 'unknown'),
                'duration': call_data.get('duration', 0),
                'transcript': call_data.get('transcript', ''),
                'summary': call_data.get('summary', ''),
                'recording_url': call_data.get('recordingUrl', ''),
                'created_at': call_data.get('createdAt', ''),
                'ended_reason': call_data.get('endedReason', '')
            }
    except:
        pass
    return None

def save_transcripts_to_db(transcripts):
    """Save transcripts to Supabase for dashboard display"""
    print(f"💾 Saving {len(transcripts)} transcripts to database...")
    
    for t in transcripts:
        try:
            # Store in a transcripts table or update leads
            supabase.table("system_logs").insert({
                'level': 'call_transcript',
                'message': json.dumps({
                    'call_id': t['id'],
                    'customer': t['customer_name'],
                    'phone': t['customer_phone'],
                    'status': t['status'],
                    'duration_sec': t['duration'],
                    'transcript': t['transcript'][:2000] if t['transcript'] else '',
                    'summary': t['summary'],
                    'recording_url': t['recording_url'],
                    'ended_reason': t['ended_reason']
                }),
                'timestamp': t['created_at']
            }).execute()
            print(f"  ✅ Saved: {t['customer_name']}")
        except Exception as e:
            print(f"  ❌ Error saving {t['customer_name']}: {e}")

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║      📞 FETCHING TODAY'S CALL TRANSCRIPTS                ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Get today's calls
    calls = fetch_todays_calls()
    
    if not calls:
        print("No calls found for today")
        return
    
    # Get transcripts for each call
    transcripts = []
    for call in calls:
        call_id = call.get('id')
        if call_id:
            print(f"  Fetching transcript: {call_id[:8]}...")
            t = get_call_transcript(call_id)
            if t:
                transcripts.append(t)
    
    # Display summary
    print(f"\n📊 TODAY'S CALL SUMMARY:")
    print(f"Total Calls: {len(transcripts)}")
    
    for t in transcripts:
        status_emoji = "✅" if t['status'] == 'ended' else "⏳"
        duration = t['duration'] or 0
        print(f"  {status_emoji} {t['customer_name']} - {duration}s - {t['ended_reason']}")
        if t['summary']:
            print(f"      Summary: {t['summary'][:100]}...")
    
    # Save to database
    if transcripts:
        save_transcripts_to_db(transcripts)
    
    # Output JSON for dashboard
    output_file = 'todays_transcripts.json'
    with open(output_file, 'w') as f:
        json.dump(transcripts, f, indent=2)
    print(f"\n📁 Saved to {output_file}")
    
    print(f"\n🔗 View at: https://www.aiserviceco.com/dashboard.html")

if __name__ == "__main__":
    main()
