# call_analytics_report.py - Full breakdown of all calls
import os
from dotenv import load_dotenv
from supabase import create_client
from collections import Counter

load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

s = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("CAMPAIGN CALL ANALYTICS REPORT")
print("=" * 60)

# Get all call transcripts
calls = s.table('call_transcripts').select('*').order('created_at', desc=True).execute()

if not calls.data:
    print("\nNo calls found in database.")
else:
    print(f"\nTotal Calls in Database: {len(calls.data)}")
    
    # Analyze outcomes
    outcomes = []
    for c in calls.data:
        summary = c.get('summary', '') or ''
        
        # Categorize based on summary content
        if 'silence' in summary.lower() or 'timed out' in summary.lower():
            outcomes.append('Silence/Timeout')
        elif 'hung up' in summary.lower() or 'cut short' in summary.lower() or 'abruptly' in summary.lower():
            outcomes.append('Hung Up')
        elif 'voicemail' in summary.lower() or 'machine' in summary.lower():
            outcomes.append('Voicemail')
        elif 'demo' in summary.lower() or 'interested' in summary.lower() or 'agreed' in summary.lower():
            outcomes.append('Interested')
        elif 'not interested' in summary.lower():
            outcomes.append('Not Interested')
        else:
            outcomes.append('Other')
    
    # Count outcomes
    outcome_counts = Counter(outcomes)
    
    print("\n--- OUTCOME BREAKDOWN ---")
    for outcome, count in sorted(outcome_counts.items(), key=lambda x: -x[1]):
        pct = (count / len(calls.data)) * 100
        print(f"  {outcome}: {count} ({pct:.1f}%)")
    
    # Connection rate
    connected = sum(1 for o in outcomes if o in ['Interested', 'Not Interested', 'Hung Up'])
    not_connected = sum(1 for o in outcomes if o in ['Silence/Timeout', 'Voicemail'])
    
    print(f"\n--- CONNECTION ANALYSIS ---")
    print(f"  Connected (spoke to human): {connected}")
    print(f"  Not Connected (VM/timeout): {not_connected}")
    if len(calls.data) > 0:
        print(f"  Connection Rate: {(connected/len(calls.data))*100:.1f}%")
    
    # Show each call detail
    print("\n--- INDIVIDUAL CALL DETAILS ---")
    for i, c in enumerate(calls.data, 1):
        created = c.get('created_at', 'Unknown')[:19]
        summary = (c.get('summary', 'No summary') or 'No summary')[:150]
        print(f"\n{i}. {created}")
        print(f"   {summary}...")

print("\n" + "=" * 60)
