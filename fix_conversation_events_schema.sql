-- FIX: Add missing columns to conversation_events table
-- Error: Could not find the 'event_type' column of 'conversation_events' in the schema cache
-- Add event_type column if missing
ALTER TABLE conversation_events
ADD COLUMN IF NOT EXISTS event_type TEXT;
-- Add source column if missing
ALTER TABLE conversation_events
ADD COLUMN IF NOT EXISTS source TEXT;
-- Add external_id column if missing (used for idempotency)
ALTER TABLE conversation_events
ADD COLUMN IF NOT EXISTS external_id TEXT;
-- Add payload column if missing
ALTER TABLE conversation_events
ADD COLUMN IF NOT EXISTS payload JSONB DEFAULT '{}';
-- Add summary column if missing
ALTER TABLE conversation_events
ADD COLUMN IF NOT EXISTS summary TEXT;
-- Add created_at if missing with default
ALTER TABLE conversation_events
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
-- Create unique constraint on external_id if not exists (prevents duplicates)
-- First check if constraint exists
DO $$ BEGIN IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'conversation_events_external_id_key'
) THEN
ALTER TABLE conversation_events
ADD CONSTRAINT conversation_events_external_id_key UNIQUE (external_id);
END IF;
EXCEPTION
WHEN others THEN -- Constraint may already exist or table structure prevents it
RAISE NOTICE 'Could not add unique constraint, may already exist';
END $$;
-- Grant permissions to service_role
GRANT ALL ON conversation_events TO service_role;
-- Force schema cache reload
NOTIFY pgrst,
'reload schema';
-- Verify columns exist
SELECT column_name,
    data_type
FROM information_schema.columns
WHERE table_name = 'conversation_events'
ORDER BY ordinal_position;