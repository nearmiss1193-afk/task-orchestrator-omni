-- Create the 'leads' table for our Agentic Workflow (Legacy/Landing Zone)
create table if not exists leads (
    id uuid default gen_random_uuid() primary key,
    created_at timestamp with time zone default now(),
    ghl_contact_id text unique,
    email text,
    website_url text,
    company_name text,
    agent_research jsonb,
    personalized_copy text,
    status text default 'new',
    lead_score int default 0,
    revenue_estimate text
);
-- The "Everything" Lead Table (Master Source of Truth)
create table if not exists contacts_master (
    id uuid default gen_random_uuid() primary key,
    created_at timestamp with time zone default now(),
    ghl_contact_id text unique not null,
    full_name text,
    email text,
    phone text,
    website_url text,
    -- AI Processing Data
    lead_score int default 0,
    sentiment text,
    raw_research jsonb,
    ai_strategy text,
    revenue_estimate text,
    -- Automation Tracking
    last_outreach_at timestamp with time zone,
    appointment_booked boolean default false,
    status text default 'new' -- 'nurturing', 'booked', 'closed', 'dq'
);
-- Mission 6: Lead Scoring Table
create table if not exists lead_scoring (
    id uuid default gen_random_uuid() primary key,
    company_name text,
    revenue_estimate text,
    employee_count int,
    industry text,
    vibe_score int,
    dossier jsonb,
    calculated_revenue_loss decimal(12, 2),
    roi_multiplier decimal(5, 2),
    last_enriched_at timestamp with time zone default now()
);
-- Enable Realtime
alter publication supabase_realtime
add table leads;
alter publication supabase_realtime
add table contacts_master;
alter publication supabase_realtime
add table lead_scoring;