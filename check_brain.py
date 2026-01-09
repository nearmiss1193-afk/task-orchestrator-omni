"""
Check Call Transcripts + Agent Learnings (Brain Training) - Verbose
"""
from supabase import create_client
import json

url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1OTA0MjQsImV4cCI6MjA4MjE2NjQyNH0.dluuiK-jr-3Z_oksYHS4saSthpkppLHQGnl6YtploPU"

client = create_client(url, key)

print("="*60)
print("BRAIN TRAINING STATUS CHECK")
print("="*60)

# Check call_transcripts
print("\n📞 CALL TRANSCRIPTS:")
try:
    result = client.table("call_transcripts").select("id,phone_number,sentiment,created_at,summary").order("created_at", desc=True).limit(5).execute()
    print(f"   Found: {len(result.data)} recent entries")
    for i, t in enumerate(result.data):
        print(f"\n   [{i+1}] Phone: {t.get('phone_number', 'Unknown')}")
        print(f"       Sentiment: {t.get('sentiment', 'N/A')}")
        print(f"       Date: {str(t.get('created_at', ''))[:19]}")
        summary = t.get('summary', '')
        if summary:
            print(f"       Summary: {summary[:100]}...")
except Exception as e:
    print(f"   ERROR: {e}")

# Check agent_learnings
print("\n🧠 AGENT LEARNINGS (AI Training from calls):")
try:
    result = client.table("agent_learnings").select("*").order("created_at", desc=True).limit(5).execute()
    print(f"   Found: {len(result.data)} entries")
    for i, l in enumerate(result.data):
        print(f"\n   [{i+1}] Agent: {l.get('agent_name', 'Unknown')}")
        print(f"       Topic: {l.get('topic', '')}")
        print(f"       Confidence: {l.get('confidence', 'N/A')}")
        insight = l.get('insight', '')
        if insight:
            if isinstance(insight, str):
                print(f"       Insight: {insight[:150]}...")
            else:
                print(f"       Insight: {json.dumps(insight)[:150]}...")
except Exception as e:
    print(f"   ERROR: {e}")

# Check leads count
print("\n📊 LEADS:")
try:
    result = client.table("leads").select("*", count="exact").limit(1).execute()
    print(f"   Total: {result.count}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "="*60)
print("ANSWER TO YOUR QUESTIONS:")
print("="*60)
print("""
1. TRANSCRIPTS: Stored in `call_transcripts` table
   - Populated by Modal vapi_webhook when calls complete
   - Contains full transcript, summary, sentiment analysis
   
2. BRAIN TRAINING: Stored in `agent_learnings` table
   - Modal extracts insights via Gemini AI after each call
   - Stores objections, successes, improvements, key insights
   - Used to make Sarah smarter over time
   
3. TO SEE MORE: Check Supabase dashboard > Table Editor
   - call_transcripts (call recordings)
   - agent_learnings (AI insights from calls)
""")
