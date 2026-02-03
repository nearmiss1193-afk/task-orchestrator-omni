-- Enable Extensions
create extension if not exists "vector";
-- Organizations (Tenants)
create table public.organizations (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    stripe_connect_id text,
    subscription_status text default 'inactive',
    created_at timestamp with time zone default now()
);
-- Profiles (Users)
create table public.profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    full_name text,
    org_id uuid references public.organizations(id),
    created_at timestamp with time zone default now()
);
-- Campaigns
create table public.campaigns (
    id uuid primary key default gen_random_uuid(),
    org_id uuid references public.organizations(id),
    name text not null,
    type text not null,
    -- 'outbound_call', 'email_blast'
    config jsonb default '{}'::jsonb,
    status text default 'draft',
    -- 'active', 'paused', 'completed'
    created_at timestamp with time zone default now()
);
-- Leads
create table public.leads (
    id uuid primary key default gen_random_uuid(),
    org_id uuid references public.organizations(id),
    campaign_id uuid references public.campaigns(id),
    first_name text,
    last_name text,
    email text,
    phone text,
    status text default 'new',
    -- 'contacted', 'converted', 'failed'
    metadata jsonb default '{}'::jsonb,
    created_at timestamp with time zone default now()
);
-- Tasks Queue (The Agent Dispatch)
create table public.tasks_queue (
    id uuid primary key default gen_random_uuid(),
    org_id uuid references public.organizations(id),
    task_type text not null,
    -- 'make_call', 'send_email', 'analyze_transcript'
    payload jsonb not null,
    status text default 'pending',
    -- 'processing', 'completed', 'failed'
    worker_id text,
    -- ID of the python worker that picked it up
    result jsonb,
    created_at timestamp with time zone default now(),
    updated_at timestamp with time zone default now()
);
-- Agent Presence
create table public.agent_presence (
    id uuid primary key default gen_random_uuid(),
    worker_id text unique not null,
    status text default 'offline',
    last_heartbeat timestamp with time zone default now()
);
-- RLS Policies
alter table public.organizations enable row level security;
alter table public.profiles enable row level security;
alter table public.campaigns enable row level security;
alter table public.leads enable row level security;
alter table public.tasks_queue enable row level security;
-- Basic RLS: Allow authenticated users to see their own org's data
-- Note: In production, you would need triggers to automatically assign org_id on insert
-- For now, we assume the backend (Service Role) handles critical writes, or auth.uid() mapping is strict
create policy "Users can view their own organization" on public.organizations for
select using (
        id in (
            select org_id
            from public.profiles
            where id = auth.uid()
        )
    );
create policy "Users can view profiles in their organization" on public.profiles for
select using (
        org_id in (
            select org_id
            from public.profiles
            where id = auth.uid()
        )
    );
-- Enable Realtime
-- This requires the table to be in the publication.
-- Note: You might need to run this in the Supabase Dashboard SQL Editor if migrations fail on publication alteration permissions.
alter publication supabase_realtime
add table public.tasks_queue;
alter publication supabase_realtime
add table public.agent_presence;