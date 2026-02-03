-- Incident Patterns + Auto-Heal Infrastructure Migration
-- For self-annealing reliability: detect failures, take safe actions, log everything
-- Table to track recurring error patterns
CREATE TABLE IF NOT EXISTS incident_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_hash TEXT NOT NULL UNIQUE,
    -- SHA256 of error signature
    error_type TEXT NOT NULL,
    -- e.g., 'webhook.5xx', 'ghl.timeout'
    error_source TEXT NOT NULL,
    -- 'modal', 'ghl', 'vapi', 'supabase'
    error_signature TEXT,
    -- First 200 chars of error message
    occurrence_count INTEGER DEFAULT 1,
    first_seen TIMESTAMPTZ DEFAULT now(),
    last_seen TIMESTAMPTZ DEFAULT now(),
    threshold_for_patch INTEGER DEFAULT 3,
    -- How many before auto-heal triggers
    patch_proposed BOOLEAN DEFAULT false,
    patch_applied BOOLEAN DEFAULT false,
    auto_heal_action TEXT,
    -- 'reduce_concurrency', 'route_fallback', 'alert', 'pause'
    metadata JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_incident_pattern_hash ON incident_patterns(pattern_hash);
CREATE INDEX IF NOT EXISTS idx_incident_pattern_source ON incident_patterns(error_source);
CREATE INDEX IF NOT EXISTS idx_incident_pattern_last_seen ON incident_patterns(last_seen DESC);
-- Table to track proposed patches (for review before auto-apply)
CREATE TABLE IF NOT EXISTS patch_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ DEFAULT now(),
    pattern_id UUID REFERENCES incident_patterns(id),
    proposed_action TEXT NOT NULL,
    -- 'reduce_concurrency', 'increase_timeout', 'route_fallback'
    target_component TEXT NOT NULL,
    -- 'ghl', 'vapi', 'modal', 'campaign'
    current_value JSONB,
    -- Current config
    proposed_value JSONB,
    -- Proposed new config
    confidence FLOAT DEFAULT 0.5,
    -- 0-1 confidence in fix
    status TEXT DEFAULT 'proposed',
    -- 'proposed', 'approved', 'applied', 'rolled_back'
    applied_at TIMESTAMPTZ,
    rolled_back_at TIMESTAMPTZ,
    outcome TEXT -- 'success', 'failed', 'inconclusive'
);
CREATE INDEX IF NOT EXISTS idx_patch_status ON patch_proposals(status);
CREATE INDEX IF NOT EXISTS idx_patch_pattern ON patch_proposals(pattern_id);
-- Table for canary deployments (gradual rollout of patches)
CREATE TABLE IF NOT EXISTS canary_deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ DEFAULT now(),
    patch_id UUID REFERENCES patch_proposals(id),
    canary_percent INTEGER DEFAULT 10,
    -- % of traffic using new config
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',
    -- 'running', 'promoted', 'rolled_back'
    promoted_at TIMESTAMPTZ,
    rolled_back_at TIMESTAMPTZ
);
-- System config table for runtime parameters
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now(),
    updated_by TEXT DEFAULT 'system'
);
-- Insert default config values
INSERT INTO system_config (key, value)
VALUES (
        'campaign.max_concurrency',
        '{"value": 10}'::jsonb
    ),
    ('ghl.timeout_ms', '{"value": 15000}'::jsonb),
    ('ghl.retry_count', '{"value": 3}'::jsonb),
    ('vapi.timeout_ms', '{"value": 30000}'::jsonb),
    (
        'reliability.check_interval_ms',
        '{"value": 600000}'::jsonb
    ),
    (
        'reliability.error_threshold',
        '{"value": 3}'::jsonb
    ),
    ('fallback.enabled', '{"value": true}'::jsonb) ON CONFLICT (key) DO NOTHING;
-- Function to get config value
CREATE OR REPLACE FUNCTION get_config(p_key TEXT) RETURNS JSONB AS $$ BEGIN RETURN (
        SELECT value
        FROM system_config
        WHERE key = p_key
    );
END;
$$ LANGUAGE plpgsql;
-- Function to update config (with audit trail via event_log_v2)
CREATE OR REPLACE FUNCTION update_config(
        p_key TEXT,
        p_value JSONB,
        p_updated_by TEXT DEFAULT 'system'
    ) RETURNS VOID AS $$ BEGIN
INSERT INTO system_config (key, value, updated_at, updated_by)
VALUES (p_key, p_value, now(), p_updated_by) ON CONFLICT (key) DO
UPDATE
SET value = p_value,
    updated_at = now(),
    updated_by = p_updated_by;
END;
$$ LANGUAGE plpgsql;
-- Function to record or increment incident pattern
CREATE OR REPLACE FUNCTION record_incident_pattern(
        p_pattern_hash TEXT,
        p_error_type TEXT,
        p_error_source TEXT,
        p_error_signature TEXT DEFAULT NULL
    ) RETURNS TABLE (
        id UUID,
        occurrence_count INTEGER,
        threshold_reached BOOLEAN
    ) AS $$
DECLARE v_id UUID;
v_count INTEGER;
v_threshold INTEGER;
BEGIN -- Try to update existing pattern
UPDATE incident_patterns
SET occurrence_count = incident_patterns.occurrence_count + 1,
    last_seen = now()
WHERE incident_patterns.pattern_hash = p_pattern_hash
RETURNING incident_patterns.id,
    incident_patterns.occurrence_count,
    incident_patterns.threshold_for_patch INTO v_id,
    v_count,
    v_threshold;
-- If no existing pattern, create new
IF v_id IS NULL THEN
INSERT INTO incident_patterns (
        pattern_hash,
        error_type,
        error_source,
        error_signature
    )
VALUES (
        p_pattern_hash,
        p_error_type,
        p_error_source,
        p_error_signature
    )
RETURNING incident_patterns.id,
    incident_patterns.occurrence_count,
    incident_patterns.threshold_for_patch INTO v_id,
    v_count,
    v_threshold;
END IF;
RETURN QUERY
SELECT v_id,
    v_count,
    (v_count >= v_threshold);
END;
$$ LANGUAGE plpgsql;
-- Function to propose auto-heal action
CREATE OR REPLACE FUNCTION propose_auto_heal(
        p_pattern_id UUID,
        p_action TEXT,
        p_target TEXT,
        p_current JSONB,
        p_proposed JSONB,
        p_confidence FLOAT DEFAULT 0.6
    ) RETURNS UUID AS $$
DECLARE v_proposal_id UUID;
BEGIN
INSERT INTO patch_proposals (
        pattern_id,
        proposed_action,
        target_component,
        current_value,
        proposed_value,
        confidence
    )
VALUES (
        p_pattern_id,
        p_action,
        p_target,
        p_current,
        p_proposed,
        p_confidence
    )
RETURNING id INTO v_proposal_id;
-- Mark pattern as having a proposed patch
UPDATE incident_patterns
SET patch_proposed = true
WHERE id = p_pattern_id;
RETURN v_proposal_id;
END;
$$ LANGUAGE plpgsql;
COMMENT ON TABLE incident_patterns IS 'Tracks recurring error patterns for auto-heal detection';
COMMENT ON TABLE patch_proposals IS 'Proposed fixes for detected patterns, pending approval or auto-apply';
COMMENT ON TABLE canary_deployments IS 'Gradual rollout tracking for applied patches';
COMMENT ON TABLE system_config IS 'Runtime configuration values that can be adjusted by auto-heal';