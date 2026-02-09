-- ============================================
-- 3-LAYER MEMORY ARCHITECTURE - SUPABASE SCHEMA
-- Run this in Supabase SQL Editor
-- ============================================
-- Layer A: Profile Memory (slow-changing facts)
CREATE TABLE IF NOT EXISTS contact_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ghl_contact_id TEXT UNIQUE,
    phone TEXT,
    -- normalized E.164
    email TEXT,
    company_name TEXT,
    timezone TEXT,
    profile_json JSONB DEFAULT '{}',
    -- preferences, constraints, notes
    memory_summary TEXT,
    -- 1-2 paragraph rolling summary
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_contact_phone ON contact_profiles(phone);
CREATE INDEX IF NOT EXISTS idx_contact_email ON contact_profiles(email);
-- Layer B: Conversation Memory (what happened + commitments)
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES contact_profiles(id),
    channel TEXT NOT NULL,
    -- sms|call|email|webchat
    status TEXT DEFAULT 'open',
    -- open|closed
    last_event_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_conv_contact ON conversations(contact_id);
CREATE TABLE IF NOT EXISTS conversation_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    event_type TEXT NOT NULL,
    -- sms_in|sms_out|call_start|call_end|email_in|email_out|note|booking
    source TEXT NOT NULL,
    -- ghl|vapi|resend|system
    external_id TEXT UNIQUE,
    -- prevents duplicates
    payload JSONB,
    -- raw webhook body
    summary TEXT,
    -- short summary for that event
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_event_conv ON conversation_events(conversation_id);
CREATE INDEX IF NOT EXISTS idx_event_external ON conversation_events(external_id);
-- Scheduler Job Locking (prevents overlapping runs)
CREATE TABLE IF NOT EXISTS job_locks (
    job_name TEXT PRIMARY KEY,
    locked_until TIMESTAMPTZ,
    locked_by TEXT
);
-- Enable RLS but allow service role full access
ALTER TABLE contact_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_locks ENABLE ROW LEVEL SECURITY;
-- Service role bypass policies
CREATE POLICY "Service role full access" ON contact_profiles FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON conversations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON conversation_events FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Service role full access" ON job_locks FOR ALL USING (true) WITH CHECK (true);