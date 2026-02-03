-- ============================================
-- CLOUD CONTROL PANEL: State Tables Migration
-- ============================================
-- A) system_state table - Single source of truth for all system controls
CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT DEFAULT 'system'
);
-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_system_state_updated ON system_state(updated_at DESC);
-- Seed default values
INSERT INTO system_state (key, value, updated_by)
VALUES ('CAMPAIGN_MODE', '"RUN"', 'migration'),
    ('OUTREACH_ENABLED', 'true', 'migration'),
    ('SMS_ENABLED', 'true', 'migration'),
    ('EMAIL_ENABLED', 'true', 'migration'),
    ('CALLS_ENABLED', 'true', 'migration'),
    ('MAX_BATCH_SIZE', '25', 'migration'),
    (
        'RATE_LIMITS',
        '{"sms_per_hour": 60, "email_per_hour": 30, "calls_per_hour": 15}',
        'migration'
    ),
    ('NEXT_ACTIONS', '{}', 'migration'),
    ('LAUNCH_MODE', '"BUSINESS_HOURS"', 'migration') ON CONFLICT (key) DO NOTHING;
-- B) operator_messages table - Chat history with orchestrator
CREATE TABLE IF NOT EXISTS operator_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ DEFAULT NOW(),
    role TEXT NOT NULL CHECK (role IN ('operator', 'orchestrator')),
    text TEXT NOT NULL,
    correlation_id TEXT,
    meta JSONB DEFAULT '{}'::jsonb
);
-- Create index for fast history queries
CREATE INDEX IF NOT EXISTS idx_operator_messages_ts ON operator_messages(ts DESC);
CREATE INDEX IF NOT EXISTS idx_operator_messages_correlation ON operator_messages(correlation_id);
-- ============================================
-- VERIFICATION QUERIES
-- ============================================
-- Check system_state is populated:
-- SELECT * FROM system_state ORDER BY key;
-- Check operator_messages table exists:
-- SELECT COUNT(*) FROM operator_messages;
-- View current campaign mode:
-- SELECT key, value FROM system_state WHERE key = 'CAMPAIGN_MODE';