-- Event Log Migration
-- Durable event storage with correlation tracking for workflow spans
CREATE TABLE IF NOT EXISTS event_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    type TEXT NOT NULL,
    -- task.started, call.completed, lead.created, health.check, error.occurred, deploy.completed
    source TEXT NOT NULL,
    -- modal, worker, dashboard, vapi, ghl, system
    severity TEXT NOT NULL DEFAULT 'info',
    -- debug, info, warn, error, critical
    correlation_id TEXT,
    -- Stable ID spanning entire workflow (e.g., lead journey)
    entity_id TEXT,
    -- ID of the specific entity (lead_id, call_id, task_id)
    payload JSONB DEFAULT '{}'::jsonb,
    -- Full event data
    -- Indexes for common queries
    CONSTRAINT valid_severity CHECK (
        severity IN ('debug', 'info', 'warn', 'error', 'critical')
    )
);
-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_event_log_ts ON event_log(ts DESC);
CREATE INDEX IF NOT EXISTS idx_event_log_type ON event_log(type);
CREATE INDEX IF NOT EXISTS idx_event_log_correlation ON event_log(correlation_id)
WHERE correlation_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_event_log_entity ON event_log(entity_id)
WHERE entity_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_event_log_severity ON event_log(severity)
WHERE severity IN ('warn', 'error', 'critical');
-- Enable Row Level Security (optional, configure as needed)
ALTER TABLE event_log ENABLE ROW LEVEL SECURITY;
-- Policy for service role access
CREATE POLICY "Service role full access" ON event_log FOR ALL TO service_role USING (true) WITH CHECK (true);
-- Policy for anon read access (for dashboard)
CREATE POLICY "Anon read access" ON event_log FOR
SELECT TO anon USING (true);
-- Function to get events for a correlation chain
CREATE OR REPLACE FUNCTION get_correlation_timeline(p_correlation_id TEXT) RETURNS TABLE (
        id UUID,
        ts TIMESTAMPTZ,
        type TEXT,
        source TEXT,
        severity TEXT,
        entity_id TEXT,
        payload JSONB
    ) AS $$ BEGIN RETURN QUERY
SELECT e.id,
    e.ts,
    e.type,
    e.source,
    e.severity,
    e.entity_id,
    e.payload
FROM event_log e
WHERE e.correlation_id = p_correlation_id
ORDER BY e.ts ASC;
END;
$$ LANGUAGE plpgsql;
-- Cleanup function for old events (optional, run via cron)
CREATE OR REPLACE FUNCTION cleanup_old_events(days_to_keep INTEGER DEFAULT 90) RETURNS INTEGER AS $$
DECLARE deleted_count INTEGER;
BEGIN
DELETE FROM event_log
WHERE ts < now() - (days_to_keep || ' days')::INTERVAL
    AND severity NOT IN ('error', 'critical');
GET DIAGNOSTICS deleted_count = ROW_COUNT;
RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;
COMMENT ON TABLE event_log IS 'Durable event log with correlation tracking for workflow spans';
COMMENT ON COLUMN event_log.correlation_id IS 'Stable ID that spans an entire workflow (e.g., from lead creation to call completion)';
COMMENT ON COLUMN event_log.entity_id IS 'Specific entity this event relates to (lead_id, call_id, task_id)';