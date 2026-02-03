-- ==========================================================
-- KICKOFF RUNS TABLE
-- One-time per-day campaign execution tracking
-- ==========================================================
CREATE TABLE IF NOT EXISTS kickoff_runs (
    date DATE PRIMARY KEY,
    executed BOOLEAN NOT NULL DEFAULT false,
    executed_at TIMESTAMPTZ,
    run_id TEXT,
    contacts_reached INT DEFAULT 0,
    details JSONB DEFAULT '{}'::jsonb
);
-- Index for fast lookup
CREATE INDEX IF NOT EXISTS idx_kickoff_runs_executed ON kickoff_runs(date, executed);
-- Enable RLS
ALTER TABLE kickoff_runs ENABLE ROW LEVEL SECURITY;
-- Policy for service role access
CREATE POLICY "Service can manage kickoff_runs" ON kickoff_runs FOR ALL USING (true) WITH CHECK (true);
-- Grant access
GRANT SELECT,
    INSERT,
    UPDATE,
    DELETE ON kickoff_runs TO service_role;
-- ==========================================================
-- INSERT TOMORROW'S KICKOFF (run this once to schedule)
-- ==========================================================
INSERT INTO kickoff_runs (date, executed)
VALUES (CURRENT_DATE + INTERVAL '1 day', false) ON CONFLICT (date) DO NOTHING;