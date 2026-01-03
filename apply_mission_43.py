import os
import time
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

sql_query = """
-- Mission 43: Sovereign Reflection Cycle
CREATE TABLE IF NOT EXISTS public.reflection_logs (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    epoch_date date DEFAULT CURRENT_DATE,
    created_at timestamptz DEFAULT now(),
    avg_gain_variance float,
    avg_uptime float,
    redundancy_efficiency float,
    content text,
    directives jsonb,
    trend_sentiment text 
);
ALTER TABLE public.reflection_logs ENABLE ROW LEVEL SECURITY;
-- Check policy to avoid dupes
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'reflection_logs' AND policyname = 'Service Role Full Access Reflection') THEN
        CREATE POLICY "Service Role Full Access Reflection" ON public.reflection_logs AS PERMISSIVE FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;
END $$;
"""

print("[Bridge] Attempting to apply Mission 43 Schema (Block 6)...")
try:
    response = supabase.rpc("exec_sql", {"query": sql_query}).execute()
    print("✅ SUCCESS: Reflection Table Created.")
except Exception as e:
    print(f"❌ BRIDGE FAILED: {e}")
