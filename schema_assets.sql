-- Asset Inbox Schema
-- Purpose: Store videos, links, and documents for Antigravity to process.
CREATE TABLE IF NOT EXISTS asset_inbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    -- 'video', 'link', 'image', 'document'
    url TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    -- 'pending', 'processing', 'completed', 'trash'
    category VARCHAR(50),
    -- 'email', 'marketing', 'research', 'other'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Enable RLS
ALTER TABLE asset_inbox ENABLE ROW LEVEL SECURITY;
-- Simple policy for service role / authenticated users
CREATE POLICY "Enable all for service role" ON asset_inbox USING (true) WITH CHECK (true);