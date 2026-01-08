
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Supabase credentials missing.")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_transcripts():
    print("🧠 Checking 'call_transcripts' table for recent learning data...")
    
    try:
        # Fetch last 5 transcripts
        res = supabase.table('call_transcripts').select('*').order('created_at', desc=True).limit(5).execute()
        transcripts = res.data
        
        if not transcripts:
            print("❌ No transcripts found. The Brain is starving.")
            return

        print(f"✅ Found {len(transcripts)} recent transcripts:")
        for t in transcripts:
            print(f"  - [{t.get('created_at')}] ID: {t.get('call_id')} | Status: {t.get('status')} | Duration: {t.get('duration_seconds')}s")
            print(f"    Summary: {t.get('summary', 'No summary yet')[:100]}...")
            
    except Exception as e:
        print(f"❌ Error reading table: {e}")

if __name__ == "__main__":
    check_transcripts()
