-- SOVEREIGN DASHBOARD FUNCTIONAL UPGRADE: SCHEMA UPDATE
-- Date: 2026-01-22
-- Target: contacts_master
-- 1. Call Transcripts for Sarah 2.0
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS call_transcript TEXT;
-- 2. Individualized Audit Report URLs (AEO)
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS audit_report_url TEXT;
-- 3. Last Outreach Content (SMS/Email Body Persistence)
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS last_outreach_body TEXT;
-- 4. Outreach Metadata (Timestamp of last contact)
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS last_outreach_at TIMESTAMPTZ;
-- 5. Comments/Logs for manual review
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS notes TEXT;
COMMENT ON COLUMN contacts_master.call_transcript IS 'Full transcript of the Vapi Sarah 2.0 call';
COMMENT ON COLUMN contacts_master.audit_report_url IS 'Public/Secure link to the AEO visibility audit';