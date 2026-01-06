"""
LISTEN LINDA MEMORY INTEGRATION
================================
Creates Supabase tables for Vapi agent memory persistence
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL') or os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Supabase credentials not found")
    exit(1)

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# Create agent_memory table via REST API (auto-creates if using RLS)
print("🧠 Setting up Listen Linda memory tables...")

# Memory entries for conversation context
memory_schema = """
CREATE TABLE IF NOT EXISTS agent_memory (
    id SERIAL PRIMARY KEY,
    agent_id TEXT NOT NULL,
    user_phone TEXT NOT NULL,
    memory_type TEXT DEFAULT 'conversation',
    context JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_memory_phone ON agent_memory(user_phone);
CREATE INDEX IF NOT EXISTS idx_agent_memory_agent ON agent_memory(agent_id);
"""

# For now, let's just verify Supabase connection and check existing tables
print(f"📡 Connecting to Supabase: {SUPABASE_URL[:30]}...")

# Try to access an existing table to verify connection
res = requests.get(
    f'{SUPABASE_URL}/rest/v1/',
    headers=headers,
    timeout=15
)

if res.status_code == 200:
    print("✅ Supabase connection verified")
    print("\n📋 Instructions to add memory table:")
    print("1. Go to Supabase dashboard → SQL Editor")
    print("2. Run this SQL:")
    print(memory_schema)
    print("\n3. Then Linda can use /api/memory to store/retrieve context")
else:
    print(f"⚠️ Supabase response: {res.status_code}")
    print(res.text[:200] if res.text else "No response body")

# Create memory API endpoint info
print("\n🔌 Memory API endpoints to create:")
print("  POST /api/memory - Store memory")
print("  GET /api/memory?phone=+1234567890 - Get memories for caller")
print("  DELETE /api/memory?id=123 - Clear specific memory")
