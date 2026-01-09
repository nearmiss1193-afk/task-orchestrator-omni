import psycopg2

DB_URL = 'postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres'

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

print("Creating missing tables for AI learning...")

# Create agent_learnings table
cur.execute("""
    CREATE TABLE IF NOT EXISTS agent_learnings (
        id SERIAL PRIMARY KEY,
        agent_name TEXT NOT NULL,
        topic TEXT,
        insight TEXT,
        confidence FLOAT DEFAULT 0.8,
        created_at TIMESTAMP DEFAULT NOW()
    )
""")
print("✓ Created agent_learnings table")

# Create call_transcripts table
cur.execute("""
    CREATE TABLE IF NOT EXISTS call_transcripts (
        id SERIAL PRIMARY KEY,
        call_id TEXT UNIQUE,
        phone_number TEXT,
        assistant_id TEXT,
        transcript TEXT,
        summary TEXT,
        sentiment TEXT,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    )
""")
print("✓ Created call_transcripts table")

# Create system_logs if missing
cur.execute("""
    CREATE TABLE IF NOT EXISTS system_logs (
        id SERIAL PRIMARY KEY,
        level TEXT DEFAULT 'INFO',
        message TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )
""")
print("✓ Created system_logs table")

# Create calendar_events if missing
cur.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id SERIAL PRIMARY KEY,
        title TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        attendees TEXT,
        status TEXT DEFAULT 'scheduled',
        created_at TIMESTAMP DEFAULT NOW()
    )
""")
print("✓ Created calendar_events table")

# Create training_data if missing
cur.execute("""
    CREATE TABLE IF NOT EXISTS training_data (
        id SERIAL PRIMARY KEY,
        source TEXT,
        content TEXT,
        category TEXT,
        verified BOOLEAN DEFAULT false,
        created_at TIMESTAMP DEFAULT NOW()
    )
""")
print("✓ Created training_data table")

conn.commit()

# Now check what we have
print("\n" + "=" * 50)
print("CURRENT DATABASE STATE")
print("=" * 50)

cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' 
    ORDER BY table_name
""")
tables = [r[0] for r in cur.fetchall()]

for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM "{t}"')
    count = cur.fetchone()[0]
    marker = "✓" if count > 0 else "-"
    print(f"  {marker} {t}: {count}")

# Brain summary
print("\n🧠 BRAIN ENTRIES:")
cur.execute("SELECT key FROM system_memory")
for r in cur.fetchall():
    print(f"  - {r[0]}")

conn.close()
print("\n✅ Database ready for AI learning!")
