-- Campaign Runs Table Migration
-- Purpose: Track campaign executions for dashboard visibility
CREATE TABLE IF NOT EXISTS campaign_runs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    run_id TEXT NOT NULL,
    campaign_type TEXT NOT NULL DEFAULT 'outreach',
    status TEXT NOT NULL DEFAULT 'pending',
    -- pending, running, completed, failed, paused
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    leads_targeted INTEGER DEFAULT 0,
    messages_sent INTEGER DEFAULT 0,
    messages_failed INTEGER DEFAULT 0,
    variant_id TEXT,
    variant_name TEXT,
    vertical TEXT DEFAULT 'hvac',
    payload JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- System State Table (key/value for cloud control)
CREATE TABLE IF NOT EXISTS system_state (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by TEXT DEFAULT 'system'
);
-- Campaign Queue Table
CREATE TABLE IF NOT EXISTS campaign_queue (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'queued',
    -- queued, running, completed, failed, cancelled
    campaign_type TEXT NOT NULL DEFAULT 'sms',
    planned_for TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    priority INTEGER DEFAULT 5,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_campaign_runs_status ON campaign_runs(status);
CREATE INDEX IF NOT EXISTS idx_campaign_runs_started_at ON campaign_runs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaign_queue_status ON campaign_queue(status);
CREATE INDEX IF NOT EXISTS idx_campaign_queue_planned ON campaign_queue(planned_for);
-- Insert initial system state
INSERT INTO system_state (key, value, updated_by)
VALUES ('campaign_mode', '"idle"', 'migration'),
    ('outreach_enabled', 'true', 'migration'),
    ('sms_enabled', 'true', 'migration'),
    ('email_enabled', 'true', 'migration'),
    ('voice_enabled', 'true', 'migration'),
    (
        'last_health_check',
        '{"status": "pending"}',
        'migration'
    ) ON CONFLICT (key) DO NOTHING;
-- Call Transcripts Table (for P4)
CREATE TABLE IF NOT EXISTS call_transcripts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    call_id TEXT UNIQUE NOT NULL,
    from_number TEXT,
    to_number TEXT,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    disposition TEXT,
    summary TEXT,
    transcript TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_call_transcripts_call_id ON call_transcripts(call_id);
CREATE INDEX IF NOT EXISTS idx_call_transcripts_ended_at ON call_transcripts(ended_at DESC);