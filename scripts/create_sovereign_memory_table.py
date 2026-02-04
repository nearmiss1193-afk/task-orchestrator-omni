"""
Direct PostgreSQL table creation for sovereign_memory
Uses DATABASE_URL to connect directly to Supabase PostgreSQL
"""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

print(f"🔗 Connecting to database...")

try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 not installed. Installing...")
    import subprocess
    subprocess.run(["pip", "install", "psycopg2-binary"], check=True)
    import psycopg2

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Create the table
sql = """
CREATE TABLE IF NOT EXISTS sovereign_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    section TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    source TEXT DEFAULT 'system',
    CONSTRAINT unique_section_key UNIQUE (section, key)
);

CREATE INDEX IF NOT EXISTS idx_sovereign_memory_section ON sovereign_memory(section);
CREATE INDEX IF NOT EXISTS idx_sovereign_memory_key ON sovereign_memory(key);
"""

print("📝 Creating sovereign_memory table...")
cur.execute(sql)
conn.commit()
print("✅ Table created successfully!")

# Verify
cur.execute("SELECT COUNT(*) FROM sovereign_memory")
count = cur.fetchone()[0]
print(f"📊 Table has {count} rows")

cur.close()
conn.close()
print("✅ Done!")
