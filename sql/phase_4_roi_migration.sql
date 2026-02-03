-- Add deal_value column to contacts_master
-- Default value of 497 (Standard Audit/Service Price)
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS deal_value NUMERIC DEFAULT 497;
-- Add lead_source for attribution if missing
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS lead_source TEXT DEFAULT 'direct-audit';
-- Create an outreach_billing table to track costs
CREATE TABLE IF NOT EXISTS system_billing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ts TIMESTAMPTZ DEFAULT NOW(),
    item_type TEXT,
    -- 'vapi_call', 'gemini_tokens', 'ghl_sms'
    item_cost NUMERIC,
    payload JSONB
);