-- SELF-HEALING LEARNING DATABASE SCHEMA
-- Run this in Supabase SQL Editor to create the learning infrastructure
-- Build Logs: Track every deployment and outcome
CREATE TABLE IF NOT EXISTS build_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    deployment_id TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    service TEXT NOT NULL,
    what_changed TEXT,
    outcome TEXT CHECK (outcome IN ('success', 'failure', 'partial')),
    error_message TEXT,
    fix_applied TEXT,
    time_to_fix_minutes INTEGER,
    metadata JSONB DEFAULT '{}'
);
-- Failure Patterns: Recognized error signatures and solutions
CREATE TABLE IF NOT EXISTS failure_patterns (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pattern_id TEXT UNIQUE NOT NULL,
    error_signature TEXT NOT NULL,
    root_cause TEXT NOT NULL,
    solution TEXT NOT NULL,
    times_seen INTEGER DEFAULT 1,
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    auto_fixable BOOLEAN DEFAULT FALSE,
    fix_success_rate FLOAT DEFAULT 0,
    metadata JSONB DEFAULT '{}'
);
-- External Knowledge: Learned best practices from docs
CREATE TABLE IF NOT EXISTS external_knowledge (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source TEXT NOT NULL,
    topic TEXT NOT NULL,
    knowledge TEXT NOT NULL,
    applies_to TEXT,
    added_date TIMESTAMPTZ DEFAULT NOW(),
    relevance_score FLOAT DEFAULT 0.5
);
-- Recovery Playbook: Step-by-step recovery procedures
CREATE TABLE IF NOT EXISTS recovery_playbook (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    issue_type TEXT NOT NULL,
    step_number INTEGER NOT NULL,
    action TEXT NOT NULL,
    verification TEXT NOT NULL,
    fallback TEXT,
    timeout_seconds INTEGER DEFAULT 30,
    UNIQUE(issue_type, step_number)
);
-- System Health Log: Real-time health tracking
CREATE TABLE IF NOT EXISTS system_health_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    service TEXT NOT NULL,
    status TEXT CHECK (
        status IN ('healthy', 'degraded', 'down', 'recovering')
    ),
    response_time_ms INTEGER,
    error_message TEXT,
    recovery_attempted BOOLEAN DEFAULT FALSE,
    recovery_successful BOOLEAN,
    metadata JSONB DEFAULT '{}'
);
-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_failure_patterns_signature ON failure_patterns USING gin(to_tsvector('english', error_signature));
CREATE INDEX IF NOT EXISTS idx_system_health_timestamp ON system_health_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_build_logs_timestamp ON build_logs(timestamp DESC);
-- SEED KNOWN FAILURE PATTERNS
INSERT INTO failure_patterns (
        pattern_id,
        error_signature,
        root_cause,
        solution,
        auto_fixable,
        fix_success_rate
    )
VALUES (
        'modal_cold_start',
        'Failed to fetch|ECONNREFUSED|504 Gateway Timeout|timeout|modal-http: invalid',
        'Modal function went cold and did not wake up in time (cold start timeout)',
        'Hit health endpoint 3x with 30s timeout each, then redeploy if still failing',
        TRUE,
        0.85
    ),
    (
        'api_base_mismatch',
        'Dashboard shows ERROR but direct Modal URL works|API_BASE mismatch',
        'Dashboard hardcoded wrong URL after Modal redeployment changed the URL',
        'Update API_BASE in dashboard.html to match current Modal deployment URL',
        TRUE,
        0.95
    ),
    (
        'supabase_connection_lost',
        'relation does not exist|connection refused to supabase|JWT expired',
        'Supabase free tier paused or connection pool exhausted or auth expired',
        'Check Supabase dashboard, restore if paused, refresh connection',
        FALSE,
        0.0
    ),
    (
        'vapi_sdk_blocked',
        'Vapi is not defined|SDK not loaded|net::ERR_BLOCKED_BY_CLIENT',
        'Vapi CDN blocked by ad blocker, CSP, or network policy',
        'Check CSP headers, add Vapi domains to allowlist, use local SDK fallback',
        TRUE,
        0.7
    ),
    (
        'cors_blocking',
        'CORS|Access-Control-Allow-Origin|preflight|blocked by CORS policy',
        'Backend not sending proper CORS headers for dashboard domain',
        'Verify CORS headers include dashboard domain, redeploy Modal with fixed headers',
        TRUE,
        0.9
    ) ON CONFLICT (pattern_id) DO NOTHING;
-- SEED RECOVERY PLAYBOOKS
INSERT INTO recovery_playbook (
        issue_type,
        step_number,
        action,
        verification,
        fallback,
        timeout_seconds
    )
VALUES (
        'modal_cold_start',
        1,
        'ping_health_endpoint_3x',
        'health_returns_200',
        'wait_30_seconds',
        30
    ),
    (
        'modal_cold_start',
        2,
        'trigger_modal_warmup',
        'response_time_under_5s',
        'continue',
        60
    ),
    (
        'modal_cold_start',
        3,
        'redeploy_modal_app',
        'deployment_successful',
        'alert_human',
        120
    ),
    (
        'api_base_mismatch',
        1,
        'get_current_modal_url',
        'url_retrieved',
        'use_known_url',
        10
    ),
    (
        'api_base_mismatch',
        2,
        'update_dashboard_api_base',
        'file_updated',
        'alert_human',
        30
    ),
    (
        'api_base_mismatch',
        3,
        'deploy_to_vercel',
        'vercel_deployment_live',
        'alert_human',
        120
    ),
    (
        'vapi_sdk_blocked',
        1,
        'check_csp_headers',
        'vapi_domains_allowed',
        'add_csp_headers',
        10
    ),
    (
        'vapi_sdk_blocked',
        2,
        'verify_local_sdk_fallback',
        'local_sdk_exists',
        'download_sdk_locally',
        30
    ),
    (
        'vapi_sdk_blocked',
        3,
        'deploy_to_vercel',
        'sdk_loads_successfully',
        'alert_human',
        120
    ),
    (
        'cors_blocking',
        1,
        'check_modal_cors_config',
        'cors_configured',
        'add_cors_headers',
        10
    ),
    (
        'cors_blocking',
        2,
        'redeploy_modal_app',
        'cors_headers_present',
        'alert_human',
        120
    ) ON CONFLICT (issue_type, step_number) DO NOTHING;
-- Enable RLS but allow service role full access
ALTER TABLE build_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE failure_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE external_knowledge ENABLE ROW LEVEL SECURITY;
ALTER TABLE recovery_playbook ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_health_log ENABLE ROW LEVEL SECURITY;
-- Create policies for service role
CREATE POLICY "Service role full access" ON build_logs FOR ALL USING (true);
CREATE POLICY "Service role full access" ON failure_patterns FOR ALL USING (true);
CREATE POLICY "Service role full access" ON external_knowledge FOR ALL USING (true);
CREATE POLICY "Service role full access" ON recovery_playbook FOR ALL USING (true);
CREATE POLICY "Service role full access" ON system_health_log FOR ALL USING (true);