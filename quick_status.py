"""
quick_status.py - Fast campaign status check
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

print("=" * 60)
print("CAMPAIGN STATUS REPORT")
print("=" * 60)

# Lead counts by status
cur.execute("""
    SELECT status, COUNT(*) 
    FROM leads 
    GROUP BY status 
    ORDER BY COUNT(*) DESC
""")
print("\n📊 LEADS BY STATUS:")
for row in cur.fetchall():
    print(f"   {row[0]}: {row[1]}")

# Emails sent
cur.execute("SELECT COUNT(*) FROM outbound_events WHERE event_type='email'")
emails = cur.fetchone()[0]
print(f"\n📧 EMAILS SENT: {emails}")

# SMS sent  
cur.execute("SELECT COUNT(*) FROM outbound_events WHERE event_type='sms'")
sms = cur.fetchone()[0] if cur.rowcount else 0
print(f"💬 SMS SENT: {sms}")

# Calls made
cur.execute("SELECT COUNT(*) FROM outbound_events WHERE event_type='call'")
calls = cur.fetchone()[0] if cur.rowcount else 0
print(f"📞 CALLS MADE: {calls}")

# Recent transcripts
cur.execute("""
    SELECT contact_name, summary, created_at 
    FROM transcripts 
    ORDER BY created_at DESC 
    LIMIT 5
""")
print("\n🎙️ RECENT TRANSCRIPTS:")
for row in cur.fetchall():
    print(f"   - {row[0]}: {row[1][:60]}... ({row[2]})")

conn.close()
print("\n" + "=" * 60)
