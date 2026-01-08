"""
CREATE SUPABASE TABLE VIA SQL RPC
Uses Supabase's pg_query to execute raw SQL
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
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

CREATE INDEX IF NOT EXISTS idx_call_transcripts_call_id ON call_transcripts(call_id);
CREATE INDEX IF NOT EXISTS idx_call_transcripts_assistant ON call_transcripts(assistant_id);
CREATE INDEX IF NOT EXISTS idx_call_transcripts_created ON call_transcripts(created_at DESC);
"""

def execute_sql():
    """Execute SQL via Supabase RPC"""
    print("🗄️ Creating call_transcripts table via Supabase...")
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Use the sql RPC endpoint if available
    # First try to insert a test record to see if table exists
    test_payload = {
        "call_id": "test_check_if_exists",
        "transcript": "test"
    }
    
    res = requests.post(
        f"{SUPABASE_URL}/rest/v1/call_transcripts",
        headers=headers,
        json=test_payload,
        timeout=30
    )
    
    if res.status_code in [200, 201]:
        # Table exists, delete the test record
        requests.delete(
            f"{SUPABASE_URL}/rest/v1/call_transcripts?call_id=eq.test_check_if_exists",
            headers=headers
        )
        print("✅ Table 'call_transcripts' exists and is accessible!")
        return True
    elif res.status_code == 404:
        print("⚠️ Table doesn't exist yet.")
        print("\n📋 COPY THIS SQL TO SUPABASE SQL EDITOR:")
        print("=" * 60)
        print(CREATE_TABLE_SQL)
        print("=" * 60)
        print(f"\n🔗 Open: https://supabase.com/dashboard/project/rzcpfwkygdvoshtwxncs/sql/new")
        return False
    else:
        # Check if it's a constraint violation (table exists but unique constraint)
        if "duplicate key" in res.text or "already exists" in res.text.lower():
            print("✅ Table exists (duplicate key error confirms it)")
            return True
        print(f"❓ Response: {res.status_code} - {res.text[:200]}")
        return False

if __name__ == "__main__":
    execute_sql()
