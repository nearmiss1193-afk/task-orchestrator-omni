import os
import time
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

sql_query = """
-- Mission 39: Dynamic Engine Registry
CREATE TABLE IF NOT EXISTS public.engine_registry (
    engine_name text PRIMARY KEY,
    latency_ms int DEFAULT 0,
    uptime_24h float DEFAULT 100.0,
    error_rate float DEFAULT 0.0,
    priority_score float DEFAULT 1.0,
    last_updated timestamptz DEFAULT now()
);

ALTER TABLE public.engine_registry ENABLE ROW LEVEL SECURITY;
-- Check if policy exists before creating (Postgres limitation) or use DO block
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'engine_registry' AND policyname = 'Service Role Full Access Engines') THEN
        CREATE POLICY "Service Role Full Access Engines" ON public.engine_registry AS PERMISSIVE FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;
END $$;

INSERT INTO public.engine_registry (engine_name, latency_ms, uptime_24h, error_rate, priority_score)
VALUES 
    ('gemini-flash', 500, 99.5, 0.05, 0.95),
    ('anti-gravity', 200, 99.9, 0.01, 1.2),
    ('heuristic-mock', 10, 100.0, 0.0, 0.5) 
ON CONFLICT (engine_name) DO NOTHING;
"""

print("[Bridge] Attempting to apply Mission 39 Registry...")
try:
    response = supabase.rpc("exec_sql", {"query": sql_query}).execute()
    print("✅ SUCCESS: Registry Table Created.")
except Exception as e:
    print(f"❌ BRIDGE FAILED: {e}")
