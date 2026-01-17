-- Job Runs Migration
-- Tracks scheduled job executions with idempotency and catch-up support
CREATE TABLE IF NOT EXISTS job_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_name TEXT NOT NULL,
    -- 'campaign', 'prospect', 'optimize', 'kpi_snapshot', 'reliability_check'
    scheduled_for DATE NOT NULL,
    -- The date this run was scheduled for
    window_id TEXT,
    -- '8am_ct', '12pm_ct', etc. for multiple runs per day
    ran_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status TEXT NOT NULL DEFAULT 'success',
    -- 'success', 'fail', 'skipped', 'catchup'
    details JSONB DEFAULT '{}'::jsonb,
    -- Ensure one run per job per day per window
    CONSTRAINT unique_job_run UNIQUE (job_name, scheduled_for, window_id)
);
CREATE INDEX IF NOT EXISTS idx_job_runs_name ON job_runs(job_name);
CREATE INDEX IF NOT EXISTS idx_job_runs_date ON job_runs(scheduled_for DESC);
CREATE INDEX IF NOT EXISTS idx_job_runs_status ON job_runs(status);
-- Send Windows Configuration
CREATE TABLE IF NOT EXISTS send_windows (
    id SERIAL PRIMARY KEY,
    channel TEXT NOT NULL UNIQUE,
    -- 'phone', 'sms', 'email'
    weekdays_only BOOLEAN DEFAULT true,
    start_hour INTEGER NOT NULL,
    -- 24-hour format, recipient local time
    end_hour INTEGER NOT NULL,
    extra_rules JSONB DEFAULT '{}'::jsonb,
    -- e.g., {"friday_end": 12, "break_start": 11, "break_end": 13}
    active BOOLEAN DEFAULT true
);
-- Insert default send windows
INSERT INTO send_windows (
        channel,
        weekdays_only,
        start_hour,
        end_hour,
        extra_rules
    )
VALUES ('phone', true, 9, 18, '{}'),
    ('sms', true, 9, 19, '{}'),
    (
        'email',
        true,
        8,
        16,
        '{"friday_end": 12, "break_start": 11, "break_end": 13}'
    ) ON CONFLICT (channel) DO NOTHING;
-- Helper function to check if today's job ran
CREATE OR REPLACE FUNCTION job_ran_today(
        p_job_name TEXT,
        p_window_id TEXT DEFAULT '8am_ct'
    ) RETURNS BOOLEAN AS $$ BEGIN RETURN EXISTS (
        SELECT 1
        FROM job_runs
        WHERE job_name = p_job_name
            AND scheduled_for = CURRENT_DATE
            AND window_id = p_window_id
            AND status IN ('success', 'catchup')
    );
END;
$$ LANGUAGE plpgsql;
-- Helper function to record a job run
CREATE OR REPLACE FUNCTION record_job_run(
        p_job_name TEXT,
        p_window_id TEXT DEFAULT '8am_ct',
        p_status TEXT DEFAULT 'success',
        p_details JSONB DEFAULT '{}'::jsonb
    ) RETURNS UUID AS $$
DECLARE new_id UUID;
BEGIN
INSERT INTO job_runs (
        job_name,
        scheduled_for,
        window_id,
        status,
        details
    )
VALUES (
        p_job_name,
        CURRENT_DATE,
        p_window_id,
        p_status,
        p_details
    ) ON CONFLICT (job_name, scheduled_for, window_id) DO
UPDATE
SET ran_at = now(),
    status = p_status,
    details = p_details
RETURNING id INTO new_id;
RETURN new_id;
END;
$$ LANGUAGE plpgsql;
-- Function to check if current time is within send window
CREATE OR REPLACE FUNCTION is_in_send_window(
        p_channel TEXT,
        p_recipient_hour INTEGER,
        -- Hour in recipient's local time
        p_recipient_weekday INTEGER,
        -- 0=Sunday, 1=Monday, etc.
        p_override BOOLEAN DEFAULT false
    ) RETURNS BOOLEAN AS $$
DECLARE window send_windows;
BEGIN -- Override bypasses window check
IF p_override THEN RETURN true;
END IF;
SELECT * INTO window
FROM send_windows
WHERE channel = p_channel
    AND active = true;
IF NOT FOUND THEN RETURN true;
-- No window defined, allow
END IF;
-- Check weekday (1-5 = Mon-Fri)
IF window.weekdays_only
AND (
    p_recipient_weekday = 0
    OR p_recipient_weekday = 6
) THEN RETURN false;
END IF;
-- Check hour
IF p_recipient_hour < window.start_hour
OR p_recipient_hour >= window.end_hour THEN RETURN false;
END IF;
-- Check Friday special rules for email
IF p_channel = 'email'
AND p_recipient_weekday = 5 THEN IF (window.extra_rules->>'friday_end')::INTEGER IS NOT NULL
AND p_recipient_hour >= (window.extra_rules->>'friday_end')::INTEGER THEN RETURN false;
END IF;
END IF;
-- Check break period for email
IF p_channel = 'email' THEN IF (window.extra_rules->>'break_start')::INTEGER IS NOT NULL
AND (window.extra_rules->>'break_end')::INTEGER IS NOT NULL
AND p_recipient_hour >= (window.extra_rules->>'break_start')::INTEGER
AND p_recipient_hour < (window.extra_rules->>'break_end')::INTEGER THEN RETURN false;
END IF;
END IF;
RETURN true;
END;
$$ LANGUAGE plpgsql;
COMMENT ON TABLE job_runs IS 'Tracks scheduled job executions for idempotency and catch-up';
COMMENT ON TABLE send_windows IS 'Send window configurations by channel';