-- ============================================================
-- VARIANT ATTRIBUTION SCHEMA MIGRATION
-- Run in Supabase SQL Editor
-- ============================================================
-- 1. Outbound Touches - records every outbound SMS/email with variant
CREATE TABLE IF NOT EXISTS outbound_touches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ DEFAULT NOW(),
    phone TEXT NOT NULL,
    channel TEXT NOT NULL CHECK (channel IN ('sms', 'email', 'call')),
    variant_id TEXT,
    variant_name TEXT,
    run_id TEXT,
    vertical TEXT DEFAULT 'hvac',
    company TEXT,
    status TEXT DEFAULT 'sent',
    correlation_id TEXT,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_outbound_touches_phone ON outbound_touches(phone);
CREATE INDEX IF NOT EXISTS idx_outbound_touches_ts ON outbound_touches(ts DESC);
CREATE INDEX IF NOT EXISTS idx_outbound_touches_variant ON outbound_touches(variant_id);
-- 2. Outreach Attribution - links appointments back to touches
CREATE TABLE IF NOT EXISTS outreach_attribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id TEXT NOT NULL,
    phone TEXT,
    attributed_variant_id TEXT,
    attributed_variant_name TEXT,
    attributed_run_id TEXT,
    attributed_touch_id UUID REFERENCES outbound_touches(id),
    attributed_touch_ts TIMESTAMPTZ,
    attributed_channel TEXT,
    attribution_confidence FLOAT DEFAULT 0.0,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes
CREATE INDEX IF NOT EXISTS idx_outreach_attribution_appointment ON outreach_attribution(appointment_id);
CREATE INDEX IF NOT EXISTS idx_outreach_attribution_variant ON outreach_attribution(attributed_variant_id);
-- 3. Enable Row Level Security (optional but recommended)
ALTER TABLE outbound_touches ENABLE ROW LEVEL SECURITY;
ALTER TABLE outreach_attribution ENABLE ROW LEVEL SECURITY;
-- Allow service role full access
CREATE POLICY IF NOT EXISTS "Service role has full access to outbound_touches" ON outbound_touches FOR ALL USING (true);
CREATE POLICY IF NOT EXISTS "Service role has full access to outreach_attribution" ON outreach_attribution FOR ALL USING (true);
-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================
-- Check tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('outbound_touches', 'outreach_attribution');
-- Count rows
SELECT 'outbound_touches' as tbl,
    COUNT(*)
FROM outbound_touches
UNION ALL
SELECT 'outreach_attribution',
    COUNT(*)
FROM outreach_attribution;