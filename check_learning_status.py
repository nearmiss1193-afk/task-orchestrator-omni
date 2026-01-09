"""
Check AI Learning + Persistence Status
"""
import psycopg2

conn = psycopg2.connect('postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres')
cur = conn.cursor()

print("="*60)
print("AI LEARNING + PERSISTENCE STATUS")
print("="*60)

# Check agent_learnings
try:
    cur.execute("SELECT COUNT(*) FROM agent_learnings")
    learnings = cur.fetchone()[0]
    print(f"Agent Learnings: {learnings} entries")
    if learnings > 0:
        cur.execute("SELECT agent_name, topic, created_at FROM agent_learnings ORDER BY created_at DESC LIMIT 5")
        for row in cur.fetchall():
            print(f"  - {row[0]}: {row[1]} ({row[2]})")
except Exception as e:
    print(f"Agent Learnings: Table missing or error - {e}")

# Check system_memory (brain persistence)
try:
    cur.execute("SELECT COUNT(*) FROM system_memory")
    memory = cur.fetchone()[0]
    print(f"System Memory: {memory} entries")
except Exception as e:
    print(f"System Memory: Table missing or error - {e}")

# Check call_transcripts
try:
    cur.execute("SELECT COUNT(*) FROM call_transcripts")
    transcripts = cur.fetchone()[0]
    print(f"Call Transcripts: {transcripts}")

    if transcripts > 0:
        cur.execute("SELECT phone_number, sentiment, created_at FROM call_transcripts ORDER BY created_at DESC LIMIT 3")
        print("Recent Calls:")
        for row in cur.fetchall():
            print(f"  - {row[0]} ({row[1]}) at {row[2]}")
except Exception as e:
    print(f"Call Transcripts: Error - {e}")

# Check leads
try:
    cur.execute("SELECT COUNT(*) FROM leads")
    leads = cur.fetchone()[0]
    print(f"Total Leads: {leads}")
except Exception as e:
    print(f"Leads: Error - {e}")

conn.close()
print("="*60)
print("ASSESSMENT:")
print("- If Agent Learnings = 0: Modal webhook not triggering or calls not happening")
print("- If Transcripts exist but no Learnings: Gemini extraction may be failing")
print("="*60)
