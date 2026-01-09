
import os
import re
import time
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Supabase credentials missing.")
    exit()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def parse_and_sync_calls(logfile="campaign_status.txt"):
    if not os.path.exists(logfile):
        print(f"❌ File not found: {logfile}")
        return

    with open(logfile, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find call blocks
    # === CALL TRANSCRIPTS (10) ===
    #   - 2026-01-09T15:22:59
    #     Phone: ?
    #     Duration: ?s
    #     Outcome: ?
    #     Snippet: ...
    
    # We'll split by "  - 20" to find entries
    entries = re.split(r'\n  - (\d{4}-\d{2}-\d{2}T)', content)
    
    count = 0
    # First chunk is header, skip.
    # Entries come in pairs: date_string, body
    for i in range(1, len(entries), 2):
        date_str = entries[i]
        body = entries[i+1]
        
        full_date = date_str + body.split('\n')[0].strip() # Reconstruct date if needed, but date_str is the capture group "2026..."
        # Actually split keeps the capture group.
        # entries[1] is Date, entries[2] is remainder
        
        timestamp = date_str # e.g. 2026-01-09T15:22:59
        
        # Extract fields
        phone_match = re.search(r'Phone: (.*?)\n', body)
        snippet_match = re.search(r'Snippet: (.*?)\n', body, re.DOTALL)
        
        phone = phone_match.group(1).strip() if phone_match else "Unknown"
        snippet = snippet_match.group(1).strip() if snippet_match else "No transcript available."
        
        # Approximate sentiment
        sentiment = "Neutral"
        if "great" in snippet.lower() or "sure" in snippet.lower() or "demo" in snippet.lower():
            sentiment = "Positive"
        
        # Insert into DB
        # Table: call_transcripts (id, call_id, phone_number, summary, sentiment, created_at)
        
        data = {
            "call_id": f"call_{timestamp.replace(':','').replace('-','')}",
            "phone_number": phone if phone != "?" else "Unknown Source",
            "summary": snippet[:500], # Truncate for safety
            "sentiment": sentiment,
            "created_at": timestamp
        }
        
        # Check existing
        existing = supabase.table('call_transcripts').select('id').eq('call_id', data['call_id']).execute()
        
        if not existing.data:
            supabase.table('call_transcripts').insert(data).execute()
            print(f"✅ Synced call at {timestamp}")
            count += 1
        else:
            print(f"  Skipping existing call {timestamp}")

    print(f"Synced {count} calls.")

if __name__ == "__main__":
    parse_and_sync_calls()
