# get_transcripts.py - Fetch latest call transcripts
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

s = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=== LATEST CALL TRANSCRIPTS ===\n")

calls = s.table('call_transcripts').select('*').order('created_at', desc=True).limit(10).execute()

if not calls.data:
    print("No call transcripts found.")
else:
    for c in calls.data:
        print(f"Time: {c.get('created_at', 'Unknown')}")
        print(f"Lead ID: {c.get('lead_id', 'Unknown')}")
        print(f"Duration: {c.get('duration_seconds', 'N/A')}s")
        print(f"Outcome: {c.get('outcome', 'N/A')}")
        summary = c.get('summary', 'No summary available')
        if summary:
            print(f"Summary: {summary[:300]}...")
        print("-" * 50)

print(f"\nTotal transcripts shown: {len(calls.data)}")
