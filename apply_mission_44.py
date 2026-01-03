import os
import time
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

sql_query = """
-- Block 7: Reflection Parser
CREATE TABLE IF NOT EXISTS public.reflection_parser (
    epoch_id text PRIMARY KEY,
    date_range text,
    avg_gain float,
    uptime_percent float,
    drift_index float,
    redundancy_efficiency float,
    snapshot_integrity float,
    high_gain_missions jsonb DEFAULT '[]'::jsonb,
    low_gain_missions jsonb DEFAULT '[]'::jsonb,
    success_correlations jsonb DEFAULT '[]'::jsonb,
    common_anomalies jsonb DEFAULT '[]'::jsonb,
    heuristics_introduced jsonb DEFAULT '[]'::jsonb,
    routing_changes jsonb DEFAULT '[]'::jsonb,
    lesson_summary text,
    next_epoch_focus text,
    created_at timestamptz DEFAULT now(),
    checksum_hash text
);
ALTER TABLE public.reflection_parser ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'reflection_parser' AND policyname = 'Service Role Access Parser') THEN
        CREATE POLICY "Service Role Access Parser" ON public.reflection_parser AS PERMISSIVE FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;
END $$;

-- Block 8: Heuristic Rules
CREATE TABLE IF NOT EXISTS public.heuristic_rules (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at timestamptz DEFAULT now(),
    source text,
    insight text,
    directive text,
    weight float DEFAULT 1.0,
    active boolean DEFAULT true
);
ALTER TABLE public.heuristic_rules ENABLE ROW LEVEL SECURITY;
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename = 'heuristic_rules' AND policyname = 'Service Role Access Heuristics') THEN
        CREATE POLICY "Service Role Access Heuristics" ON public.heuristic_rules AS PERMISSIVE FOR ALL TO service_role USING (true) WITH CHECK (true);
    END IF;
END $$;
"""

print("[Bridge] Applying Mission 44 Schema (Blocks 7 & 8)...")
try:
    response = supabase.rpc("exec_sql", {"query": sql_query}).execute()
    print("✅ SUCCESS: Parser & Heuristics Tables Created.")
except Exception as e:
    print(f"❌ BRIDGE FAILED: {e}")
