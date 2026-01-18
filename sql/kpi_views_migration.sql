-- KPI Views Migration
-- Creates daily aggregate views and health check function
-- ============================================================
-- VIEW: kpi_daily
-- Daily aggregates of key events for dashboard and analytics
-- ============================================================
CREATE OR REPLACE VIEW kpi_daily AS
SELECT DATE(ts) as day,
    COUNT(*) FILTER (
        WHERE type = 'appointment.created'
    ) as appointments_booked,
    COUNT(*) FILTER (
        WHERE type = 'appointment.updated'
            AND payload->>'status' = 'confirmed'
    ) as appointments_confirmed,
    COUNT(*) FILTER (
        WHERE type = 'call.answered'
    ) as calls_answered,
    COUNT(*) FILTER (
        WHERE type = 'call.missed'
    ) as calls_missed,
    COUNT(*) FILTER (
        WHERE type = 'sms.sent'
    ) as sms_sent,
    COUNT(*) FILTER (
        WHERE type = 'sms.failed'
    ) as sms_failed,
    COUNT(*) FILTER (
        WHERE type LIKE 'lead.%'
    ) as leads_total,
    COUNT(*) FILTER (
        WHERE severity = 'error'
    ) as errors,
    COUNT(*) FILTER (
        WHERE severity = 'critical'
    ) as critical_errors,
    COUNT(*) as total_events
FROM event_log_v2
GROUP BY DATE(ts)
ORDER BY day DESC;
COMMENT ON VIEW kpi_daily IS 'Daily KPI aggregates from event_log_v2';
-- ============================================================
-- VIEW: job_runs_daily  
-- Daily job execution summary for monitoring
-- ============================================================
CREATE OR REPLACE VIEW job_runs_daily AS
SELECT scheduled_for as day,
    COUNT(*) FILTER (
        WHERE job_name = 'campaign'
            AND status = 'success'
    ) as campaign_success,
    COUNT(*) FILTER (
        WHERE job_name = 'campaign'
            AND status = 'catchup'
    ) as campaign_catchup,
    COUNT(*) FILTER (
        WHERE job_name = 'campaign'
            AND status = 'fail'
    ) as campaign_fail,
    COUNT(*) FILTER (
        WHERE job_name = 'campaign'
            AND status = 'skipped'
    ) as campaign_skipped,
    COUNT(*) FILTER (
        WHERE job_name = 'prospect'
            AND status = 'success'
    ) as prospect_success,
    COUNT(*) FILTER (
        WHERE job_name = 'prospect'
            AND status = 'fail'
    ) as prospect_fail,
    COUNT(*) FILTER (
        WHERE job_name = 'optimize'
            AND status = 'success'
    ) as optimize_success,
    COUNT(*) FILTER (
        WHERE job_name = 'kpi_snapshot'
    ) as kpi_snapshots,
    COUNT(*) FILTER (
        WHERE job_name = 'reliability_check'
    ) as reliability_checks,
    COUNT(*) as total_runs
FROM job_runs
GROUP BY scheduled_for
ORDER BY day DESC;
COMMENT ON VIEW job_runs_daily IS 'Daily job execution summary from job_runs';
-- ============================================================
-- FUNCTION: kpi_health_check()
-- Returns missing/failed jobs and error spikes for alerting
-- ============================================================
CREATE OR REPLACE FUNCTION kpi_health_check() RETURNS TABLE (
        issue_type TEXT,
        severity TEXT,
        description TEXT,
        details JSONB,
        detected_at TIMESTAMPTZ
    ) AS $$
DECLARE today DATE := CURRENT_DATE;
current_hour INTEGER := EXTRACT(
    HOUR
    FROM NOW()
);
errors_24h INTEGER;
errors_prev_24h INTEGER;
campaign_ran BOOLEAN;
BEGIN -- Check 1: Campaign didn't run today (after 9 AM)
IF current_hour >= 9 THEN
SELECT EXISTS(
        SELECT 1
        FROM job_runs
        WHERE job_name = 'campaign'
            AND scheduled_for = today
            AND status IN ('success', 'catchup')
    ) INTO campaign_ran;
IF NOT campaign_ran THEN RETURN QUERY
SELECT 'missing_job'::TEXT,
    'critical'::TEXT,
    'Campaign did not run today'::TEXT,
    jsonb_build_object(
        'job_name',
        'campaign',
        'expected_window',
        '8am_ct'
    ),
    NOW();
END IF;
END IF;
-- Check 2: Error spike (2x increase vs prev 24h)
SELECT COUNT(*) INTO errors_24h
FROM event_log_v2
WHERE severity IN ('error', 'critical')
    AND ts > NOW() - INTERVAL '24 hours';
SELECT COUNT(*) INTO errors_prev_24h
FROM event_log_v2
WHERE severity IN ('error', 'critical')
    AND ts BETWEEN NOW() - INTERVAL '48 hours'
    AND NOW() - INTERVAL '24 hours';
IF errors_24h > 5
AND errors_24h > (errors_prev_24h * 2) THEN RETURN QUERY
SELECT 'error_spike'::TEXT,
    'warning'::TEXT,
    'Error rate increased significantly'::TEXT,
    jsonb_build_object(
        'errors_24h',
        errors_24h,
        'errors_prev_24h',
        errors_prev_24h,
        'ratio',
        ROUND(
            errors_24h::NUMERIC / GREATEST(errors_prev_24h, 1),
            2
        )
    ),
    NOW();
END IF;
-- Check 3: No KPI snapshots in last 30 minutes
IF NOT EXISTS(
    SELECT 1
    FROM event_log_v2
    WHERE type = 'kpi.snapshot'
        AND ts > NOW() - INTERVAL '30 minutes'
) THEN RETURN QUERY
SELECT 'stale_kpi'::TEXT,
    'warning'::TEXT,
    'No KPI snapshots in last 30 minutes'::TEXT,
    jsonb_build_object('expected_interval', '10 minutes'),
    NOW();
END IF;
-- Check 4: Zero appointments in last 7 days
IF NOT EXISTS(
    SELECT 1
    FROM event_log_v2
    WHERE type = 'appointment.created'
        AND ts > NOW() - INTERVAL '7 days'
) THEN RETURN QUERY
SELECT 'no_appointments'::TEXT,
    'warning'::TEXT,
    'No appointments booked in last 7 days'::TEXT,
    jsonb_build_object('primary_kpi', 'appointments_booked'),
    NOW();
END IF;
RETURN;
END;
$$ LANGUAGE plpgsql;
COMMENT ON FUNCTION kpi_health_check IS 'Returns system health issues: missing jobs, error spikes, stale KPIs';