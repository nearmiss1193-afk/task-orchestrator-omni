-- SQL to create click_events table for analytics
-- Run this in Supabase SQL Editor
CREATE TABLE IF NOT EXISTS click_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    campaign_id TEXT,
    cta_type TEXT,
    target_url TEXT,
    success BOOLEAN DEFAULT true,
    status_code INTEGER,
    source TEXT DEFAULT 'email',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes for performance queries
CREATE INDEX IF NOT EXISTS idx_click_events_created_at ON click_events(created_at);
CREATE INDEX IF NOT EXISTS idx_click_events_campaign ON click_events(campaign_id);
CREATE INDEX IF NOT EXISTS idx_click_events_success ON click_events(success);
-- Disable RLS for simplicity
ALTER TABLE click_events DISABLE ROW LEVEL SECURITY;
-- Grant anonymous access
GRANT SELECT,
    INSERT ON click_events TO anon;
GRANT SELECT,
    INSERT ON click_events TO authenticated;