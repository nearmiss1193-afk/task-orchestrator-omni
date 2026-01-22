-- Empire Analytics Schema Upgrade
-- Adds outcome tracking, A/B testing, and engagement metrics
-- Add outcome tracking columns
ALTER TABLE public.contacts_master
ADD COLUMN IF NOT EXISTS outcome TEXT DEFAULT NULL;
ALTER TABLE public.contacts_master
ADD COLUMN IF NOT EXISTS outcome_at TIMESTAMPTZ DEFAULT NULL;
-- Add A/B testing columns
ALTER TABLE public.contacts_master
ADD COLUMN IF NOT EXISTS ab_variant TEXT DEFAULT NULL;
ALTER TABLE public.contacts_master
ADD COLUMN IF NOT EXISTS ab_assigned_at TIMESTAMPTZ DEFAULT NULL;
-- Add engagement tracking
ALTER TABLE public.contacts_master
ADD COLUMN IF NOT EXISTS contact_attempts INT DEFAULT 0;
ALTER TABLE public.contacts_master
ADD COLUMN IF NOT EXISTS last_response_at TIMESTAMPTZ DEFAULT NULL;
-- Add index for outcome filtering
CREATE INDEX IF NOT EXISTS idx_contacts_outcome ON public.contacts_master(outcome);
-- Add index for A/B variant analysis
CREATE INDEX IF NOT EXISTS idx_contacts_ab_variant ON public.contacts_master(ab_variant);
-- Comment on new columns for documentation
COMMENT ON COLUMN public.contacts_master.outcome IS 'Final result: answered, voicemail, callback, booked, closed, lost';
COMMENT ON COLUMN public.contacts_master.ab_variant IS 'A/B test variant: A, B, C, or control';
COMMENT ON COLUMN public.contacts_master.contact_attempts IS 'Number of outreach attempts made';