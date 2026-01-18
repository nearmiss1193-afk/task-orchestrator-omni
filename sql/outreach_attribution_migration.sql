-- ==========================================================
-- OUTREACH ATTRIBUTION TABLE
-- Track variant attribution for bookings and learning
-- ==========================================================
-- Create table
CREATE TABLE IF NOT EXISTS outreach_attribution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    contact_id TEXT,
    phone TEXT,
    channel TEXT NOT NULL,
    variant_id TEXT,
    variant_name TEXT,
    correlation_id TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
-- Indexes for efficient lookup
CREATE INDEX IF NOT EXISTS idx_outreach_attribution_contact_id ON outreach_attribution(contact_id);
CREATE INDEX IF NOT EXISTS idx_outreach_attribution_phone ON outreach_attribution(phone);
CREATE INDEX IF NOT EXISTS idx_outreach_attribution_ts_desc ON outreach_attribution(ts DESC);
CREATE INDEX IF NOT EXISTS idx_outreach_attribution_variant_id ON outreach_attribution(variant_id);
-- Enable RLS
ALTER TABLE outreach_attribution ENABLE ROW LEVEL SECURITY;
-- Policy for service role access
CREATE POLICY "Service can manage outreach_attribution" ON outreach_attribution FOR ALL USING (true) WITH CHECK (true);
-- ==========================================================
-- ATTRIBUTION LOOKUP FUNCTION
-- Find most recent attribution for a contact within N days
-- ==========================================================
CREATE OR REPLACE FUNCTION get_recent_attribution(
        p_contact_id TEXT DEFAULT NULL,
        p_phone TEXT DEFAULT NULL,
        p_days_back INT DEFAULT 14
    ) RETURNS TABLE (
        id UUID,
        ts TIMESTAMPTZ,
        contact_id TEXT,
        phone TEXT,
        channel TEXT,
        variant_id TEXT,
        variant_name TEXT,
        correlation_id TEXT,
        metadata JSONB
    ) AS $$ BEGIN RETURN QUERY
SELECT a.id,
    a.ts,
    a.contact_id,
    a.phone,
    a.channel,
    a.variant_id,
    a.variant_name,
    a.correlation_id,
    a.metadata
FROM outreach_attribution a
WHERE a.ts > now() - (p_days_back || ' days')::interval
    AND (
        (
            p_contact_id IS NOT NULL
            AND a.contact_id = p_contact_id
        )
        OR (
            p_phone IS NOT NULL
            AND a.phone = p_phone
        )
    )
ORDER BY a.ts DESC
LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
-- ==========================================================
-- VARIANT BOOKING METRICS VIEW
-- Aggregate bookings by variant for learning
-- ==========================================================
CREATE OR REPLACE VIEW variant_booking_metrics AS
SELECT oa.variant_id,
    oa.variant_name,
    COUNT(DISTINCT e.entity_id) as bookings,
    MAX(e.ts) as last_booking_ts,
    COUNT(DISTINCT oa.id) as total_outreach,
    ROUND(
        COUNT(DISTINCT e.entity_id)::NUMERIC / NULLIF(COUNT(DISTINCT oa.id), 0) * 100,
        2
    ) as booking_rate_percent
FROM outreach_attribution oa
    LEFT JOIN event_log_v2 e ON e.type = 'outcome.booking'
    AND e.payload->>'variant_id' = oa.variant_id
    AND e.ts > now() - interval '7 days'
WHERE oa.ts > now() - interval '7 days'
    AND oa.variant_id IS NOT NULL
GROUP BY oa.variant_id,
    oa.variant_name
ORDER BY bookings DESC,
    booking_rate_percent DESC;
-- Grant access
GRANT SELECT ON variant_booking_metrics TO anon;
GRANT SELECT,
    INSERT,
    UPDATE,
    DELETE ON outreach_attribution TO service_role;
GRANT EXECUTE ON FUNCTION get_recent_attribution TO service_role;