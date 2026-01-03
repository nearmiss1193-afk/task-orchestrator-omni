-- CORTEX v2.0 Migration: Social Accounts (Fixed)
CREATE TABLE IF NOT EXISTS public.social_accounts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    platform TEXT NOT NULL,
    username TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    credentials JSONB
);
-- Security
ALTER TABLE public.social_accounts ENABLE ROW LEVEL SECURITY;
-- Policies
CREATE POLICY "Allow All" ON public.social_accounts FOR ALL USING (true);
-- Notification
NOTIFY pgrst,
'reload config';