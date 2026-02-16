-- SOCIAL LOGS MIGRATION
-- Records every social broadcast for the real-time dashboard feed.
CREATE TABLE IF NOT EXISTS social_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES contacts_master(id) ON DELETE
    SET NULL,
        platform VARCHAR(50) NOT NULL,
        content TEXT NOT NULL,
        status VARCHAR(20) DEFAULT 'published',
        broadcast_id TEXT,
        video_url TEXT,
        published_at TIMESTAMPTZ DEFAULT NOW(),
        metadata JSONB DEFAULT '{}'::jsonb
);
-- Index for fast lead lookup
CREATE INDEX IF NOT EXISTS idx_social_logs_lead ON social_logs(lead_id);
CREATE INDEX IF NOT EXISTS idx_social_logs_platform ON social_logs(platform);
CREATE INDEX IF NOT EXISTS idx_social_logs_timestamp ON social_logs(published_at DESC);
-- Enable RLS (Service role has full access by default)
ALTER TABLE social_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS "Service role has full access" ON social_logs FOR ALL USING (true);