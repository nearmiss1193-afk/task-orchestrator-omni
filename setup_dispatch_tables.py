"""Setup script: Create dispatch_jobs and tech_roster tables in Supabase."""
import sys; sys.path.insert(0, ".")
from dotenv import load_dotenv; load_dotenv()
from modules.database.supabase_client import get_supabase

sb = get_supabase()

# We can't run raw SQL via the Python client, so we'll use RPC or just verify
# Tables need to be created via Supabase SQL editor. Here's the SQL:

SQL = """
-- Run this in Supabase SQL Editor (https://supabase.com/dashboard → SQL Editor)

CREATE TABLE IF NOT EXISTS dispatch_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    service_type TEXT NOT NULL,
    address TEXT NOT NULL,
    customer_name TEXT,
    customer_phone TEXT,
    company_name TEXT,
    urgency TEXT DEFAULT 'standard',
    notes TEXT,
    assigned_tech_id TEXT,
    assigned_tech_name TEXT,
    assigned_tech_phone TEXT,
    status TEXT DEFAULT 'new',
    dispatch_attempts INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS tech_roster (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    services TEXT[] DEFAULT '{}',
    region TEXT DEFAULT 'florida',
    available BOOLEAN DEFAULT true,
    current_job_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast dispatch queries
CREATE INDEX IF NOT EXISTS idx_dispatch_jobs_status ON dispatch_jobs(status);
CREATE INDEX IF NOT EXISTS idx_tech_roster_available ON tech_roster(available);
"""

print("=" * 60)
print("DISPATCH TABLES — Run this SQL in Supabase SQL Editor")
print("=" * 60)
print(SQL)
print("=" * 60)

# Try to verify if tables already exist
try:
    r = sb.table("dispatch_jobs").select("id", count="exact").limit(0).execute()
    print(f"\n✅ dispatch_jobs table exists ({r.count or 0} rows)")
except Exception as e:
    print(f"\n❌ dispatch_jobs table NOT found — run the SQL above")

try:
    r = sb.table("tech_roster").select("id", count="exact").limit(0).execute()
    print(f"✅ tech_roster table exists ({r.count or 0} rows)")
except Exception as e:
    print(f"❌ tech_roster table NOT found — run the SQL above")
