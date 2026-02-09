-- Email Opens Tracking Table
-- Run this in Supabase SQL Editor
CREATE TABLE IF NOT EXISTS email_opens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email_id TEXT NOT NULL,
    recipient_email TEXT,
    business_name TEXT,
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address TEXT,
    user_agent TEXT,
    open_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_email_opens_email_id ON email_opens(email_id);
CREATE INDEX IF NOT EXISTS idx_email_opens_opened_at ON email_opens(opened_at);
-- Enable RLS but allow service role to insert
ALTER TABLE email_opens ENABLE ROW LEVEL SECURITY;
-- Policy for service role access
CREATE POLICY "Service role can do everything" ON email_opens FOR ALL TO service_role USING (true) WITH CHECK (true);
-- Comment
COMMENT ON TABLE email_opens IS 'Tracks email opens via tracking pixel - Added Feb 5, 2026';