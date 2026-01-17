"""
Create required Supabase tables for autonomous prospecting system
"""
import requests

SUPABASE_URL = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo'

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# SQL to create the missing tables
sql_commands = [
    """
    CREATE TABLE IF NOT EXISTS prospect_targets (
        id SERIAL PRIMARY KEY,
        industry TEXT NOT NULL,
        location TEXT NOT NULL,
        company_name TEXT,
        phone TEXT,
        email TEXT,
        website TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS cron_logs (
        id SERIAL PRIMARY KEY,
        trigger TEXT,
        action TEXT,
        result JSONB,
        timestamp TIMESTAMPTZ DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS optimization_logs (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMPTZ DEFAULT NOW(),
        analysis JSONB,
        patterns_found INTEGER
    );
    """,
    """
    ALTER TABLE contacts_master ADD COLUMN IF NOT EXISTS personal_audit TEXT;
    """,
    """
    ALTER TABLE contacts_master ADD COLUMN IF NOT EXISTS touch_count INTEGER DEFAULT 0;
    """,
    """
    ALTER TABLE contacts_master ADD COLUMN IF NOT EXISTS last_contacted TIMESTAMPTZ;
    """
]

print("🔧 Creating/updating Supabase tables...")

for i, sql in enumerate(sql_commands):
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/rpc/exec_sql',
        headers=headers,
        json={'query': sql.strip()},
        timeout=30
    )
    if r.status_code in [200, 201, 204]:
        print(f"  ✅ Command {i+1} executed")
    else:
        # Try direct SQL endpoint
        print(f"  ⚠️ Command {i+1}: {r.status_code} - will try via Supabase dashboard")

print("\n📝 Note: If tables don't exist, create them via Supabase SQL Editor:")
print("https://supabase.com/dashboard/project/rzcpfwkygdvoshtwxncs/sql/new")
print("\nRequired SQL:")
print("""
CREATE TABLE IF NOT EXISTS prospect_targets (
    id SERIAL PRIMARY KEY,
    industry TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
""")
