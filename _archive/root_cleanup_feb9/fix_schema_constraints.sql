-- FIX SCHEMA CONSTRAINTS
-- ======================
-- This script fixes the "not-null" and missing column errors causing 400 Bad Request
-- when creating contacts from Phone-Only sources (SMS/Calls).
-- 1. Make ghl_contact_id NULLABLE (It is currently NOT NULL, causing crashes for new leads)
ALTER TABLE contact_profiles
ALTER COLUMN ghl_contact_id DROP NOT NULL;
-- 2. Ensure company_name column exists
ALTER TABLE contact_profiles
ADD COLUMN IF NOT EXISTS company_name TEXT;
-- 3. Ensure profile_json column exists (used for preferences)
ALTER TABLE contact_profiles
ADD COLUMN IF NOT EXISTS profile_json JSONB DEFAULT '{}';
-- 4. Verify/Refresh Permissions
GRANT ALL ON TABLE contact_profiles TO service_role;
GRANT ALL ON TABLE conversation_events TO service_role;
GRANT ALL ON TABLE conversations TO service_role;
-- 5. Force Schema Cache Reload
NOTIFY pgrst,
'reload schema';