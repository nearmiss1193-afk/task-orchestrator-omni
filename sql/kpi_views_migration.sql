-- KPI Views Migration v2
-- Updated views and health check per strict contract
-- ============================================================
-- 3A) View: kpi_daily
-- ============================================================
create or replace view public.kpi_daily as
select date_trunc('day', ts) as day,
    count(*) filter (
        where type = 'appointment.created'
    ) as appointments_booked,
    count(*) filter (
        where type = 'call.answered'
    ) as answered_calls,
    count(*) filter (
        where type = 'call.missed'
    ) as missed_calls,
    count(*) filter (
        where type = 'sms.sent'
    ) as sms_sent,
    count(*) filter (
        where type = 'sms.failed'
    ) as sms_failed,
    count(*) filter (
        where severity in ('error', 'critical')
            or type like '%.error'
    ) as errors
from public.event_log_v2
group by 1
order by 1 desc;
-- ============================================================
-- 3B) View: job_runs_daily
-- ============================================================
create or replace view public.job_runs_daily as
select scheduled_for as day,
    job_name,
    window_id,
    max(ran_at) as last_ran_at,
    max(status) as last_status
from public.job_runs
group by 1,
    2,
    3
order by 1 desc,
    2 asc;
-- ============================================================
-- 3C) Function: kpi_health_check()
-- Returns: missing required jobs today, error spike in last 24h
-- ============================================================
create or replace function public.kpi_health_check() returns table(issue text, detail jsonb) language plpgsql as $$
declare required_jobs text [] := array ['campaign','prospect','reliability_check','kpi_snapshot'];
j text;
begin -- missing jobs today
foreach j in array required_jobs loop if not exists (
    select 1
    from public.job_runs
    where job_name = j
        and scheduled_for = current_date
        and status in ('success', 'catchup', 'skipped')
) then issue := 'missing_job_today';
detail := jsonb_build_object('job_name', j, 'date', current_date);
return next;
end if;
end loop;
-- error spike last 24h (>= 10 errors)
if (
    select count(*)
    from public.event_log_v2
    where ts > now() - interval '24 hours'
        and (
            severity in ('error', 'critical')
            or type like '%.error'
        )
) >= 10 then issue := 'error_spike_24h';
detail := jsonb_build_object(
    'errors_24h',
    (
        select count(*)
        from public.event_log_v2
        where ts > now() - interval '24 hours'
            and (
                severity in ('error', 'critical')
                or type like '%.error'
            )
    )
);
return next;
end if;
-- ok marker
if not found then issue := 'ok';
detail := jsonb_build_object('timestamp', now());
return next;
end if;
end;
$$;
COMMENT ON VIEW public.kpi_daily IS 'Daily KPI aggregates from event_log_v2';
COMMENT ON VIEW public.job_runs_daily IS 'Daily job run summary grouped by job_name and window_id';
COMMENT ON FUNCTION public.kpi_health_check IS 'Returns missing jobs and error spikes for self-annealing';