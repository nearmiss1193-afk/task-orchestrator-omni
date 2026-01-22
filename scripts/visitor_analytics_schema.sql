-- Visitor Analytics Schema
-- Run this in Supabase SQL Editor
CREATE TABLE IF NOT EXISTS public.visitor_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    visitor_id TEXT,
    -- Fingerprint/Cookie ID
    url TEXT,
    referrer TEXT,
    user_agent TEXT,
    device_type TEXT,
    -- 'mobile', 'desktop', 'tablet'
    browser TEXT,
    os TEXT,
    ip_hash TEXT,
    -- Anonymized IP
    metadata JSONB,
    -- Any extra params (utm source etc)
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indices for analytics queries
CREATE INDEX IF NOT EXISTS idx_visitor_created_at ON public.visitor_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_visitor_url ON public.visitor_logs(url);
CREATE INDEX IF NOT EXISTS idx_visitor_device ON public.visitor_logs(device_type);
-- Enable RLS (Allow public insert for tracking, but read only for admin)
ALTER TABLE public.visitor_logs ENABLE ROW LEVEL SECURITY;
-- Allow ANYONE to insert (it's a tracking pixel essentially)
CREATE POLICY "Allow public insert" ON public.visitor_logs FOR
INSERT WITH CHECK (true);
-- Allow admins to read
CREATE POLICY "Allow authenticated read" ON public.visitor_logs FOR
SELECT USING (auth.role() = 'authenticated');