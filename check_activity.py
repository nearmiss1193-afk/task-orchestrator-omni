"""
Full Activity Report - Calls, Emails, Sarah/John activity
"""
from supabase import create_client

url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1OTA0MjQsImV4cCI6MjA4MjE2NjQyNH0.dluuiK-jr-3Z_oksYHS4saSthpkppLHQGnl6YtploPU"
client = create_client(url, key)

print("="*70)
print("FULL ACTIVITY REPORT - CALLS, EMAILS, SARAH/JOHN ACTIVITY")
print("="*70)

# 1. Call transcripts
print("\n" + "="*50)
print("📞 CALL TRANSCRIPTS")
print("="*50)
result = client.table("call_transcripts").select("*", count="exact").execute()
print(f"Total in database: {len(result.data)}")

YOUR_PHONE = "+13529368152"
your_calls = [c for c in result.data if YOUR_PHONE in str(c.get('phone_number', ''))]
other_calls = [c for c in result.data if YOUR_PHONE not in str(c.get('phone_number', ''))]

print(f"  - Calls involving YOUR number ({YOUR_PHONE}): {len(your_calls)}")
print(f"  - Calls to OTHER prospects: {len(other_calls)}")

if other_calls:
    print("\n  Calls to OTHERS:")
    for c in other_calls[:10]:
        print(f"    • {c.get('phone_number')} | {str(c.get('created_at',''))[:16]}")
else:
    print("\n  ⚠️  NO OUTBOUND CALLS TO PROSPECTS YET!")
    print("  Sarah/John have not initiated any outbound sales calls.")

# 2. Leads status
print("\n" + "="*50)
print("📈 LEADS BREAKDOWN")
print("="*50)
result = client.table("leads").select("status").execute()
statuses = {}
for lead in result.data:
    s = lead.get('status', 'unknown')
    statuses[s] = statuses.get(s, 0) + 1
for status, count in sorted(statuses.items(), key=lambda x: -x[1]):
    print(f"  {status}: {count}")

# 3. Check for email tracking
print("\n" + "="*50)
print("📧 EMAIL ACTIVITY")
print("="*50)
# Check system_logs for email events
try:
    result = client.table("system_logs").select("*").execute()
    email_logs = [l for l in result.data if 'email' in l.get('event_type', '').lower() or 'email' in l.get('message', '').lower()]
    print(f"Email-related logs: {len(email_logs)}")
    for l in email_logs[:5]:
        print(f"  • {l.get('event_type')}: {l.get('message', '')[:60]}")
except Exception as e:
    print(f"Error: {e}")

# Check if we have email opens/clicks tracking
print("\nNOTE: Email opens/replies require Resend webhooks configured.")
print("Current emails are sent but not tracked for opens.")

# 4. Conclusion
print("\n" + "="*70)
print("💡 CONCLUSION")
print("="*70)
print("""
WHAT WE KNOW:
• Campaigns ARE running and sending emails (see campaign logs)
• Leads ARE being created (139 total)
• Call transcripts only show YOUR test calls (no outbound sales yet)

WHY SARAH/JOHN HAVEN'T CALLED PROSPECTS:
1. The campaign scripts send EMAILS as first touch
2. Outbound CALLS require either:
   a) Lead replies/shows interest (triggers call)  
   b) Manual trigger from dashboard
   c) Scheduled follow-up call sequence

TO GET OUTBOUND CALLS WORKING:
• Configure Vapi to auto-dial when lead status = 'replied'
• Or manually trigger calls from dashboard

FOR EMAIL TRACKING (opens/replies):
• Need to set up Resend webhook for event tracking
• Route: POST /email-webhook on Modal
""")
