-- Mission: Nick Saraev Strategy Extensions
-- 1. Team Accountability Table
-- Tracks daily output and Revenue Per Employee (RPE)
create table if not exists team_accountability (
    id uuid default gen_random_uuid() primary key,
    created_at timestamp with time zone default now(),
    employee_name text not null,
    job_role text,
    daily_output_metric text,
    -- e.g. "Words written", "Lines of code", "Calls made"
    daily_output_value int default 0,
    rpe_calculated decimal(12, 2),
    -- Revenue Per Employee for this specific role
    notes text,
    date date default current_date
);
-- 2. Hiring Pipeline Table
-- Separates high-tier talent from sales leads
create table if not exists hiring_pipeline (
    id uuid default gen_random_uuid() primary key,
    created_at timestamp with time zone default now(),
    candidate_name text not null,
    candidate_email text unique,
    job_role text,
    cv_url text,
    status text default 'applied',
    -- 'applied', 'trial_sent', 'trial_passed', 'interview_scheduled', 'hired', 'rejected'
    ai_score int default 0,
    raw_notes jsonb,
    ghl_contact_id text unique -- Link to GHL contact if synced
);
-- Enable Realtime for these new tables
alter publication supabase_realtime
add table team_accountability;
alter publication supabase_realtime
add table hiring_pipeline;