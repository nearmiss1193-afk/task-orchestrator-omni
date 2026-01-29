-- SOVEREIGN PERSISTENT WISDOM SCHEMA
-- Stores high-level synthesized insights across leads and verticals
CREATE TABLE IF NOT EXISTS system_wisdom (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category TEXT NOT NULL,
    -- 'outreach_hook', 'industry_insight', 'objection_fix', 'competitor_intel'
    vertical TEXT DEFAULT 'general',
    topic TEXT,
    insight TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.5,
    examples JSONB DEFAULT '[]',
    -- List of successful lead IDs or snippets
    source_event_count INTEGER DEFAULT 1,
    last_validated_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
-- Index for searching relevant wisdom
CREATE INDEX IF NOT EXISTS idx_wisdom_vertical ON system_wisdom(vertical);
CREATE INDEX IF NOT EXISTS idx_wisdom_category ON system_wisdom(category);
-- RLS
ALTER TABLE system_wisdom ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role full access" ON system_wisdom FOR ALL USING (true);