-- Event Log V2 Migration
-- Creates new canonical event_log_v2 table without dropping old event_log
-- NEW CANONICAL TABLE
CREATE TABLE IF NOT EXISTS event_log_v2 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    type TEXT NOT NULL,
    -- e.g., 'lead.inbound', 'task.completed', 'error.occurred'
    source TEXT NOT NULL DEFAULT 'modal',
    -- 'modal', 'worker', 'vapi', 'ghl', 'system'
    severity TEXT NOT NULL DEFAULT 'info',
    -- 'debug', 'info', 'warn', 'error', 'critical'
    correlation_id TEXT,
    -- Stable ID spanning workflow (e.g., phone number or lead_id)
    entity_id TEXT,
    -- Specific entity ID (call_id, task_id)
    payload JSONB DEFAULT '{}'::jsonb
);
-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_event_log_v2_ts ON event_log_v2(ts DESC);
CREATE INDEX IF NOT EXISTS idx_event_log_v2_type ON event_log_v2(type);
CREATE INDEX IF NOT EXISTS idx_event_log_v2_correlation ON event_log_v2(correlation_id);
CREATE INDEX IF NOT EXISTS idx_event_log_v2_entity ON event_log_v2(entity_id);
CREATE INDEX IF NOT EXISTS idx_event_log_v2_severity ON event_log_v2(severity);
CREATE INDEX IF NOT EXISTS idx_event_log_v2_source ON event_log_v2(source);
-- Enable Row Level Security
ALTER TABLE event_log_v2 ENABLE ROW LEVEL SECURITY;
-- RLS Policies
CREATE POLICY "Service role full access" ON event_log_v2 FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Anon read access" ON event_log_v2 FOR
SELECT USING (true);
-- Compatibility view to unify old and new tables
CREATE OR REPLACE VIEW event_log_unified AS
SELECT id,
    ts,
    type,
    source,
    severity,
    correlation_id,
    entity_id,
    payload
FROM event_log_v2
UNION ALL
SELECT gen_random_uuid() as id,
    created_at as ts,
    event_type as type,
    'legacy' as source,
    CASE
        WHEN success THEN 'info'
        ELSE 'error'
    END as severity,
    phone as correlation_id,
    NULL as entity_id,
    jsonb_build_object('success', success, 'legacy', true) as payload
FROM event_log
ORDER BY ts DESC;
-- Helper function to get recent events
CREATE OR REPLACE FUNCTION get_recent_events(
        p_limit INTEGER DEFAULT 50,
        p_type TEXT DEFAULT NULL,
        p_severity TEXT DEFAULT NULL
    ) RETURNS SETOF event_log_v2 AS $$ BEGIN RETURN QUERY
SELECT *
FROM event_log_v2
WHERE (
        p_type IS NULL
        OR type = p_type
    )
    AND (
        p_severity IS NULL
        OR severity = p_severity
    )
ORDER BY ts DESC
LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
-- Function to get timeline for a correlation_id
CREATE OR REPLACE FUNCTION get_correlation_timeline(p_correlation_id TEXT) RETURNS SETOF event_log_v2 AS $$ BEGIN RETURN QUERY
SELECT *
FROM event_log_v2
WHERE correlation_id = p_correlation_id
ORDER BY ts ASC;
END;
$$ LANGUAGE plpgsql;
COMMENT ON TABLE event_log_v2 IS 'Canonical event log with structured schema';
COMMENT ON VIEW event_log_unified IS 'Unified view of old event_log and new event_log_v2';