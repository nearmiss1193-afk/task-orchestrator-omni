"""
CREATE SUPABASE TABLE: call_transcripts
Run this once to create the persistent call memory table.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

# SQL to create the call_transcripts table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS call_transcripts (
    id SERIAL PRIMARY KEY,
    call_id TEXT UNIQUE NOT NULL,
    assistant_id TEXT,
    assistant_name TEXT,
    customer_phone TEXT,
    customer_name TEXT,
    status TEXT,
    duration_seconds NUMERIC,
    transcript TEXT,
    summary TEXT,
    analysis JSONB,
    structured_data JSONB,
    success_evaluation TEXT,
    cost NUMERIC,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    learnings_extracted BOOLEAN DEFAULT FALSE
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_call_transcripts_call_id ON call_transcripts(call_id);
CREATE INDEX IF NOT EXISTS idx_call_transcripts_assistant ON call_transcripts(assistant_id);
CREATE INDEX IF NOT EXISTS idx_call_transcripts_created ON call_transcripts(created_at DESC);
"""

def create_table_via_rpc():
    """Create table using Supabase REST API with raw SQL (requires service role)"""
    print("🗄️ Creating call_transcripts table in Supabase...")
    
    # Note: Supabase REST API doesn't directly support DDL
    # We'll use a workaround by checking if we can insert/select first
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test if table exists by trying to select
    res = requests.get(
        f"{SUPABASE_URL}/rest/v1/call_transcripts?limit=1",
        headers=headers,
        timeout=30
    )
    
    if res.status_code == 200:
        print("✅ Table 'call_transcripts' already exists!")
        return True
    elif res.status_code == 404 or "relation" in res.text.lower():
        print("⚠️ Table doesn't exist. Please create it manually in Supabase Dashboard.")
        print("\n📋 SQL TO RUN IN SUPABASE SQL EDITOR:")
        print("-" * 50)
        print(CREATE_TABLE_SQL)
        print("-" * 50)
        print("\nGo to: https://supabase.com/dashboard/project/rzcpfwkygdvoshtwxncs/sql")
        return False
    else:
        print(f"❓ Status: {res.status_code}")
        print(res.text[:300])
        return False

if __name__ == "__main__":
    create_table_via_rpc()
