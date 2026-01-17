-- Auto-Patch Pipeline with Canary Deployment Migration
-- Detects incident patterns, proposes patches, runs canary, promotes/rollbacks
-- ==========================================================
-- PATCH PROPOSALS - Generated when patterns detected
-- ==========================================================
CREATE TABLE IF NOT EXISTS patch_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Trigger info
    trigger_type TEXT NOT NULL,
    -- 'incident_repeat', 'kpi_stagnation', 'manual'
    trigger_count INTEGER,
    -- Number of incidents that triggered
    trigger_pattern TEXT,
    -- Description of pattern detected
    correlation_ids TEXT [],
    -- Related event_log correlation IDs
    -- Patch details
    target_component TEXT NOT NULL,
    -- 'modal_orchestrator', 'worker', 'prompt_variant'
    diff_content TEXT,
    -- Proposed code diff
    test_content TEXT,
    -- Test code to validate patch
    rationale TEXT,
    -- Status
    status TEXT DEFAULT 'proposed',
    -- 'proposed', 'testing', 'canary', 'promoted', 'rolled_back', 'rejected'
    -- Test results
    test_passed BOOLEAN,
    test_output TEXT,
    test_run_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_patches_status ON patch_proposals(status);
CREATE INDEX IF NOT EXISTS idx_patches_created ON patch_proposals(created_at DESC);
-- ==========================================================
-- CANARY DEPLOYMENTS - Traffic splitting and monitoring
-- ==========================================================
CREATE TABLE IF NOT EXISTS canary_deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patch_id UUID REFERENCES patch_proposals(id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,
    -- Traffic config
    canary_percent INTEGER DEFAULT 5,
    -- % of traffic to canary
    -- Baseline metrics (before canary)
    baseline_error_rate FLOAT,
    baseline_kpi FLOAT,
    -- e.g., booking rate
    baseline_latency_ms INTEGER,
    -- Canary metrics (during canary)
    canary_error_rate FLOAT,
    canary_kpi FLOAT,
    canary_latency_ms INTEGER,
    canary_requests INTEGER DEFAULT 0,
    -- Decision
    decision TEXT,
    -- 'promote', 'rollback', 'extend', 'pending'
    decision_reason TEXT,
    decision_at TIMESTAMPTZ,
    -- Status
    status TEXT DEFAULT 'active' -- 'active', 'completed', 'aborted'
);
CREATE INDEX IF NOT EXISTS idx_canary_status ON canary_deployments(status)
WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_canary_patch ON canary_deployments(patch_id);
-- ==========================================================
-- INCIDENT PATTERNS - Tracks repeated issues
-- ==========================================================
CREATE TABLE IF NOT EXISTS incident_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_seen TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Pattern identification
    pattern_hash TEXT NOT NULL UNIQUE,
    -- Hash of error signature
    pattern_type TEXT,
    -- 'error', 'timeout', 'failure', 'degradation'
    component TEXT,
    error_message TEXT,
    -- Tracking
    occurrence_count INTEGER DEFAULT 1,
    threshold_for_patch INTEGER DEFAULT 3,
    patch_proposed BOOLEAN DEFAULT false,
    -- Resolution
    resolved BOOLEAN DEFAULT false,
    resolved_by_patch UUID REFERENCES patch_proposals(id)
);
CREATE INDEX IF NOT EXISTS idx_patterns_hash ON incident_patterns(pattern_hash);
CREATE INDEX IF NOT EXISTS idx_patterns_unresolved ON incident_patterns(resolved)
WHERE resolved = false;
-- ==========================================================
-- ROUTING FUNCTIONS FOR CANARY
-- ==========================================================
-- Check if request should go to canary
CREATE OR REPLACE FUNCTION should_route_to_canary() RETURNS BOOLEAN AS $$
DECLARE active_canary canary_deployments;
BEGIN
SELECT * INTO active_canary
FROM canary_deployments
WHERE status = 'active'
ORDER BY started_at DESC
LIMIT 1;
IF active_canary IS NULL THEN RETURN false;
END IF;
-- Random routing based on canary_percent
RETURN random() * 100 < active_canary.canary_percent;
END;
$$ LANGUAGE plpgsql;
-- Update canary metrics
CREATE OR REPLACE FUNCTION update_canary_metrics(
        p_is_error BOOLEAN,
        p_latency_ms INTEGER,
        p_is_conversion BOOLEAN
    ) RETURNS VOID AS $$
DECLARE active_canary canary_deployments;
BEGIN
SELECT * INTO active_canary
FROM canary_deployments
WHERE status = 'active'
LIMIT 1;
IF active_canary IS NULL THEN RETURN;
END IF;
UPDATE canary_deployments
SET canary_requests = canary_requests + 1,
    canary_error_rate = (
        canary_error_rate * canary_requests + (
            CASE
                WHEN p_is_error THEN 1
                ELSE 0
            END
        )
    ) / (canary_requests + 1),
    canary_kpi = (
        canary_kpi * canary_requests + (
            CASE
                WHEN p_is_conversion THEN 1
                ELSE 0
            END
        )
    ) / (canary_requests + 1),
    canary_latency_ms = (
        canary_latency_ms * canary_requests + p_latency_ms
    ) / (canary_requests + 1)
WHERE id = active_canary.id;
END;
$$ LANGUAGE plpgsql;
-- Evaluate canary and decide promote/rollback
CREATE OR REPLACE FUNCTION evaluate_canary(p_min_requests INTEGER DEFAULT 100) RETURNS TABLE (canary_id UUID, decision TEXT, reason TEXT) AS $$
DECLARE c canary_deployments;
BEGIN
SELECT * INTO c
FROM canary_deployments
WHERE status = 'active'
LIMIT 1;
IF c IS NULL THEN RETURN QUERY
SELECT NULL::UUID,
    'no_canary'::TEXT,
    'No active canary'::TEXT;
RETURN;
END IF;
-- Need minimum requests
IF c.canary_requests < p_min_requests THEN RETURN QUERY
SELECT c.id,
    'pending'::TEXT,
    format(
        'Need %s more requests',
        p_min_requests - c.canary_requests
    );
RETURN;
END IF;
-- Rollback if error rate increased > 10%
IF c.canary_error_rate > c.baseline_error_rate * 1.1 THEN
UPDATE canary_deployments
SET decision = 'rollback',
    decision_reason = 'Error rate regression',
    decision_at = now(),
    status = 'completed'
WHERE id = c.id;
UPDATE patch_proposals
SET status = 'rolled_back'
WHERE id = c.patch_id;
RETURN QUERY
SELECT c.id,
    'rollback'::TEXT,
    'Error rate increased by >10%'::TEXT;
RETURN;
END IF;
-- Rollback if KPI dropped > 5%
IF c.canary_kpi < c.baseline_kpi * 0.95 THEN
UPDATE canary_deployments
SET decision = 'rollback',
    decision_reason = 'KPI regression',
    decision_at = now(),
    status = 'completed'
WHERE id = c.id;
UPDATE patch_proposals
SET status = 'rolled_back'
WHERE id = c.patch_id;
RETURN QUERY
SELECT c.id,
    'rollback'::TEXT,
    'KPI dropped by >5%'::TEXT;
RETURN;
END IF;
-- Promote if error rate dropped and KPI improved
IF c.canary_error_rate <= c.baseline_error_rate
AND c.canary_kpi >= c.baseline_kpi THEN
UPDATE canary_deployments
SET decision = 'promote',
    decision_reason = 'Metrics improved',
    decision_at = now(),
    status = 'completed'
WHERE id = c.id;
UPDATE patch_proposals
SET status = 'promoted'
WHERE id = c.patch_id;
RETURN QUERY
SELECT c.id,
    'promote'::TEXT,
    'Error rate stable/down, KPI stable/up'::TEXT;
RETURN;
END IF;
RETURN QUERY
SELECT c.id,
    'extend'::TEXT,
    'Metrics inconclusive, extending canary'::TEXT;
END;
$$ LANGUAGE plpgsql;
COMMENT ON TABLE patch_proposals IS 'Auto-generated patches when incident patterns repeat';
COMMENT ON TABLE canary_deployments IS 'Traffic-split canary testing for patches';
COMMENT ON TABLE incident_patterns IS 'Tracks repeated incidents to trigger patch proposals';