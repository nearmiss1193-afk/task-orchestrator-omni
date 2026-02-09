-- VAPI Debug Logs Table
-- Created: 2026-02-08
-- Purpose: Persistent diagnostic logging for voice memory debugging
-- 
-- This table captures every Vapi webhook event with full diagnostic data
-- to identify why returning caller greetings fail.
CREATE TABLE IF NOT EXISTS vapi_debug_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    -- Event metadata
    event_type TEXT,
    -- 'assistant-request', 'end-of-call-report', etc.
    call_direction TEXT,
    -- 'inbound', 'outbound'
    -- Phone number tracking (the key issue)
    raw_phone TEXT,
    -- Exact value from Vapi payload
    normalized_phone TEXT,
    -- After normalize_phone() processing
    -- Memory lookup results
    lookup_result TEXT,
    -- 'FOUND', 'NOT_FOUND', 'ERROR', 'SKIPPED'
    customer_name_found TEXT,
    -- Name retrieved from customer_memory
    context_summary JSONB,
    -- Full context_summary JSONB from lookup
    -- Response tracking
    assistant_overrides_sent JSONB,
    -- Full assistantOverrides payload we returned
    call_mode TEXT,
    -- 'sales', 'support', 'default'
    -- Debug notes
    notes TEXT -- Any additional debug info
);
-- Index for quick lookups by phone
CREATE INDEX IF NOT EXISTS idx_vapi_debug_logs_phone ON vapi_debug_logs(normalized_phone);
CREATE INDEX IF NOT EXISTS idx_vapi_debug_logs_created ON vapi_debug_logs(created_at DESC);
-- Comment for documentation
COMMENT ON TABLE vapi_debug_logs IS 'Persistent diagnostic logs for Vapi webhook events to debug voice memory issues';