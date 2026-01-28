-- Create scheduler_logs table for tracking campaign scheduler checks
CREATE TABLE IF NOT EXISTS scheduler_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    hour INTEGER NOT NULL,
    day INTEGER NOT NULL,
    source TEXT NOT NULL DEFAULT 'edge_function',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Index for querying recent logs
CREATE INDEX IF NOT EXISTS idx_scheduler_logs_checked_at ON scheduler_logs(checked_at DESC);
-- Optional: Auto-cleanup old logs (keep last 7 days)
-- Run this as a cron job or scheduled function:
-- DELETE FROM scheduler_logs WHERE checked_at < now() - INTERVAL '7 days';
-- RLS Policy (service role only)
ALTER TABLE scheduler_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role access only" ON scheduler_logs FOR ALL USING (auth.role() = 'service_role');