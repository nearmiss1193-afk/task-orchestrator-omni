import psycopg2

DB_URL = 'postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres'

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

print("=" * 60)
print("AI LEARNING & TRANSCRIPTS CHECK")
print("=" * 60)

# Check which tables exist
print("\n📦 TABLES IN DATABASE:")
cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
""")
tables = [r[0] for r in cur.fetchall()]
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM \"{t}\"")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  ✓ {t}: {count} rows")
    else:
        print(f"  - {t}: empty")

# Check for call_transcripts
print("\n📞 CALL TRANSCRIPTS:")
if 'call_transcripts' in tables:
    cur.execute("SELECT call_id, phone_number, summary, created_at FROM call_transcripts ORDER BY created_at DESC LIMIT 5")
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"  {r[1]} - {str(r[2])[:50]}... ({r[3]})")
    else:
        print("  No transcripts yet")
else:
    print("  Table 'call_transcripts' does not exist")

# Check brain memory
print("\n🧠 BRAIN MEMORY:")
cur.execute("SELECT key FROM system_memory")
for r in cur.fetchall():
    print(f"  - {r[0]}")

# Check agent_learnings
print("\n📚 AGENT LEARNINGS:")
if 'agent_learnings' in tables:
    cur.execute("SELECT agent_name, topic, insight FROM agent_learnings ORDER BY created_at DESC LIMIT 5")
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"  [{r[0]}] {r[1]}: {str(r[2])[:50]}...")
    else:
        print("  No agent learnings recorded yet")
else:
    print("  Table 'agent_learnings' does not exist - create it to enable learning")

# Check outbound events
print("\n📤 OUTBOUND EVENTS:")
if 'outbound_events' in tables:
    cur.execute("SELECT event_type, COUNT(*) FROM outbound_events GROUP BY event_type")
    rows = cur.fetchall()
    if rows:
        for r in rows:
            print(f"  {r[0]}: {r[1]}")
    else:
        print("  No outbound events")
else:
    print("  Table 'outbound_events' does not exist")

conn.close()
print("\n" + "=" * 60)
