-- Supabase Log Dashboard Setup
-- Run this in Supabase SQL Editor to create logging tables and views
-- 1. Health Logs Table
CREATE TABLE IF NOT EXISTS health_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    component TEXT NOT NULL,
    status TEXT NOT NULL,
    action_taken TEXT,
    message TEXT
);
-- 2. Webhook Logs Table
CREATE TABLE IF NOT EXISTS webhook_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    source TEXT,
    payload JSONB,
    forwarded_to TEXT,
    result_status INTEGER
);
-- 3. Campaign Logs Table
CREATE TABLE IF NOT EXISTS campaign_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    lead_id TEXT,
    touch_type TEXT,
    disposition TEXT,
    error TEXT
);
-- 4. Metrics Export Table (for Prometheus)
CREATE TABLE IF NOT EXISTS metrics_export (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metric_name TEXT NOT NULL,
    value NUMERIC,
    labels JSONB
);
-- ==========================================
-- DASHBOARD VIEWS
-- ==========================================
-- Recent Health Events
CREATE OR REPLACE VIEW health_recent AS
SELECT timestamp,
    component,
    status,
    action_taken,
    message
FROM health_logs
ORDER BY timestamp DESC
LIMIT 100;
-- Health Status by Component (Last Hour)
CREATE OR REPLACE VIEW health_by_component AS
SELECT component,
    status,
    COUNT(*) as count,
    MAX(timestamp) as last_seen
FROM health_logs
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY component,
    status
ORDER BY component,
    count DESC;
-- Webhook Success Rate (Last 24h)
CREATE OR REPLACE VIEW webhook_success_rate AS
SELECT DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) FILTER (
        WHERE result_status = 200
    ) as success,
    COUNT(*) FILTER (
        WHERE result_status != 200
    ) as failed,
    COUNT(*) as total,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE result_status = 200
        ) / NULLIF(COUNT(*), 0),
        2
    ) as success_rate
FROM webhook_logs
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', timestamp)
ORDER BY hour DESC;
-- Campaign Conversion Funnel
CREATE OR REPLACE VIEW campaign_funnel AS
SELECT touch_type,
    disposition,
    COUNT(*) as count
FROM campaign_logs
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY touch_type,
    disposition
ORDER BY touch_type,
    count DESC;
-- System Uptime Summary
CREATE OR REPLACE VIEW system_uptime AS
SELECT component,
    COUNT(*) FILTER (
        WHERE status = 'healthy'
            OR status = 'online'
            OR status = 'ok'
    ) as healthy_checks,
    COUNT(*) as total_checks,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE status IN ('healthy', 'online', 'ok')
        ) / NULLIF(COUNT(*), 0),
        2
    ) as uptime_percent
FROM health_logs
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY component;
-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_health_logs_timestamp ON health_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_timestamp ON webhook_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_campaign_logs_timestamp ON campaign_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_health_logs_component ON health_logs(component);
-- Grant access to authenticated users
ALTER TABLE health_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_logs ENABLE ROW LEVEL SECURITY;
-- Policy: Allow service role full access
CREATE POLICY IF NOT EXISTS "Service role access" ON health_logs FOR ALL USING (true);
CREATE POLICY IF NOT EXISTS "Service role access" ON webhook_logs FOR ALL USING (true);
CREATE POLICY IF NOT EXISTS "Service role access" ON campaign_logs FOR ALL USING (true);