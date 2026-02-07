"""
Create customer_memory and conversation_logs tables in Supabase

Run this script to set up the Sarah Universal Memory database schema.
"""
import os
import sys
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)
    print(f"✅ Loaded .env from {env_path}")

# Try multiple env var names
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")

print(f"URL: {SUPABASE_URL[:30] if SUPABASE_URL else 'MISSING'}...")
print(f"KEY: {SUPABASE_KEY[:20] if SUPABASE_KEY else 'MISSING'}...")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY")
    sys.exit(1)

from supabase import create_client


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL to create tables
SQL_CUSTOMER_MEMORY = """
CREATE TABLE IF NOT EXISTS customer_memory (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) UNIQUE,
    ghl_contact_id VARCHAR(255),
    
    -- Summarized context (what Sarah should remember)
    context_summary JSONB DEFAULT '{}'::jsonb,
    
    last_interaction TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast phone lookup
CREATE INDEX IF NOT EXISTS idx_customer_memory_phone ON customer_memory(phone_number);
CREATE INDEX IF NOT EXISTS idx_customer_memory_ghl ON customer_memory(ghl_contact_id);
"""

SQL_CONVERSATION_LOGS = """
CREATE TABLE IF NOT EXISTS conversation_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customer_memory(customer_id) ON DELETE CASCADE,
    channel VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    content TEXT,
    sarah_response TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Index for customer conversation lookup
CREATE INDEX IF NOT EXISTS idx_conversation_logs_customer ON conversation_logs(customer_id);
CREATE INDEX IF NOT EXISTS idx_conversation_logs_timestamp ON conversation_logs(timestamp DESC);
"""

SQL_PROMPT_TEMPLATES = """
CREATE TABLE IF NOT EXISTS prompt_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    version INTEGER DEFAULT 1,
    base_prompt TEXT NOT NULL,
    channel_modifiers JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

print("Creating customer_memory table...")
try:
    result = supabase.rpc("exec_sql", {"sql": SQL_CUSTOMER_MEMORY}).execute()
    print("✅ customer_memory table created")
except Exception as e:
    print(f"Note: {e}")
    print("Trying direct approach...")

print("\nCreating conversation_logs table...")
try:
    result = supabase.rpc("exec_sql", {"sql": SQL_CONVERSATION_LOGS}).execute()
    print("✅ conversation_logs table created")
except Exception as e:
    print(f"Note: {e}")

print("\nCreating prompt_templates table...")
try:
    result = supabase.rpc("exec_sql", {"sql": SQL_PROMPT_TEMPLATES}).execute()
    print("✅ prompt_templates table created")
except Exception as e:
    print(f"Note: {e}")

print("\n" + "="*50)
print("⚠️  If RPC failed, run this SQL directly in Supabase SQL Editor:")
print("="*50)
print(SQL_CUSTOMER_MEMORY)
print(SQL_CONVERSATION_LOGS)
print(SQL_PROMPT_TEMPLATES)
