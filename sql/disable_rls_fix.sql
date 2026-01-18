-- QUICK FIX: Disable RLS on attribution tables
-- These are internal operational tables, not user-facing
ALTER TABLE outbound_touches DISABLE ROW LEVEL SECURITY;
ALTER TABLE outreach_attribution DISABLE ROW LEVEL SECURITY;
-- Verify
SELECT tablename,
    rowsecurity
FROM pg_tables
WHERE tablename IN ('outbound_touches', 'outreach_attribution');