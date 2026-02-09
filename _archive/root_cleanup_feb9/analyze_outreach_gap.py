"""
Direct SQL query to check outreach and lead status
"""
import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime, timezone, timedelta

load_dotenv()

db_url = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(db_url)
cur = conn.cursor()

print("="*70)
print("📊 OUTREACH & LEAD STATUS ANALYSIS")
print("="*70)

# 1. Last outreach
cur.execute("""
    SELECT ts, channel, contact_id
    FROM outbound_touches
    ORDER BY ts DESC
    LIMIT 5
""")
print("\n📧 Last 5 outreach attempts:")
for row in cur.fetchall():
    print(f"   {row[0]} | {row[1]} | Contact: {row[2]}")

# 2. Outreach count by day (last 14 days)
cur.execute("""
    SELECT DATE(ts) as day, COUNT(*) as count
    FROM outbound_touches
    WHERE ts > NOW() - INTERVAL '14 days'
    GROUP BY DATE(ts)
    ORDER BY day DESC
""")
print("\n📅 Outreach by day (last 14 days):")
for row in cur.fetchall():
    print(f"   {row[0]}: {row[1]} messages")

# 3. Lead status breakdown
cur.execute("""
    SELECT status, COUNT(*) as count
    FROM contacts_master
    GROUP BY status
    ORDER BY count DESC
""")
print("\n👥 Lead status breakdown:")
for row in cur.fetchall():
    print(f"   {row[0]}: {row[1]} leads")

# 4. Contactable leads with contact info
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(email) as has_email,
        COUNT(phone) as has_phone
    FROM contacts_master
    WHERE status IN ('new', 'research_done')
""")
row = cur.fetchone()
print(f"\n✉️  Contactable leads (new/research_done):")
print(f"   Total: {row[0]}")
print(f"   With email: {row[1]}")
print(f"   With phone: {row[2]}")

# 5. Campaign mode
cur.execute("""
    SELECT status, updated_at
    FROM system_state
    WHERE key = 'campaign_mode'
""")
row = cur.fetchone()
if row:
    print(f"\n⚙️  Campaign mode: {row[0]} (updated: {row[1]})")

conn.close()
print("\n" + "="*70)
