-- Task Execution Metrics Migration
-- Tracks tool calls, latency, failures, retries, result quality per task
CREATE TABLE IF NOT EXISTS task_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    task_type TEXT NOT NULL,
    -- 'inbound', 'outbound', 'campaign', 'prospecting'
    correlation_id TEXT,
    -- Links to event_log correlation
    -- Execution metrics
    tool_calls INTEGER DEFAULT 0,
    latency_ms INTEGER DEFAULT 0,
    failures INTEGER DEFAULT 0,
    retries INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT false,
    -- Quality metrics (0-100)
    result_quality INTEGER,
    -- Optional quality score
    -- Context
    policy_version INTEGER DEFAULT 1,
    payload JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_task_metrics_ts ON task_metrics(ts DESC);
CREATE INDEX IF NOT EXISTS idx_task_metrics_type ON task_metrics(task_type);
CREATE INDEX IF NOT EXISTS idx_task_metrics_success ON task_metrics(success);
-- Policy Weights table - controls execution behavior
CREATE TABLE IF NOT EXISTS policy_weights (
    id SERIAL PRIMARY KEY,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    active BOOLEAN DEFAULT true,
    -- Retry policy
    max_retries INTEGER DEFAULT 3,
    retry_backoff_base_ms INTEGER DEFAULT 1000,
    retry_backoff_max_ms INTEGER DEFAULT 30000,
    -- Timeout policy
    tool_timeout_ms INTEGER DEFAULT 30000,
    task_timeout_ms INTEGER DEFAULT 120000,
    -- Concurrency policy
    max_concurrent_tasks INTEGER DEFAULT 5,
    max_concurrent_tools INTEGER DEFAULT 3,
    -- Tool selection weights (sum to 1.0)
    weight_gemini FLOAT DEFAULT 0.7,
    weight_fallback FLOAT DEFAULT 0.3,
    -- Quality thresholds
    min_quality_threshold INTEGER DEFAULT 50,
    -- Metadata
    updated_by TEXT DEFAULT 'system',
    notes TEXT
);
-- Insert default policy weights
INSERT INTO policy_weights (version, notes)
VALUES (1, 'Initial default policy') ON CONFLICT DO NOTHING;
-- Optimizer run history
CREATE TABLE IF NOT EXISTS optimizer_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Metrics analyzed
    tasks_analyzed INTEGER,
    success_rate FLOAT,
    avg_latency_ms INTEGER,
    -- Changes made
    old_policy_version INTEGER,
    new_policy_version INTEGER,
    changes_made JSONB,
    -- Confidence
    confidence_score FLOAT,
    rollback_available BOOLEAN DEFAULT true
);
-- Function to get current policy
CREATE OR REPLACE FUNCTION get_active_policy() RETURNS policy_weights AS $$
SELECT *
FROM policy_weights
WHERE active = true
ORDER BY version DESC
LIMIT 1;
$$ LANGUAGE sql;
-- Function to rollback to previous policy
CREATE OR REPLACE FUNCTION rollback_policy() RETURNS BOOLEAN AS $$
DECLARE current_version INTEGER;
previous_version INTEGER;
BEGIN
SELECT version INTO current_version
FROM policy_weights
WHERE active = true
ORDER BY version DESC
LIMIT 1;
previous_version := current_version - 1;
IF previous_version < 1 THEN RETURN false;
END IF;
UPDATE policy_weights
SET active = false
WHERE version = current_version;
UPDATE policy_weights
SET active = true
WHERE version = previous_version;
RETURN true;
END;
$$ LANGUAGE plpgsql;
COMMENT ON TABLE task_metrics IS 'Tracks execution metrics per task for optimizer analysis';
COMMENT ON TABLE policy_weights IS 'Controls execution behavior (retries, timeouts, concurrency)';
COMMENT ON TABLE optimizer_runs IS 'History of optimizer adjustments to policy weights';