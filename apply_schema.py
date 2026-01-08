import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
print(f"DEBUG: DB_URL present: {bool(DB_URL)}")
supa_url = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
print(f"DEBUG: SUPABASE_URL present: {bool(supa_url)}")

sql_commands = [
    """
    create table if not exists public.tasks_queue (
        id uuid primary key default gen_random_uuid(),
        org_id uuid, -- Made nullable for flexibility or foreign keys check
        task_type text not null,
        payload jsonb not null,
        status text default 'pending',
        worker_id text,
        result jsonb,
        created_at timestamp with time zone default now(),
        updated_at timestamp with time zone default now()
    );
    """,
    """
    create table if not exists public.agent_presence (
        id uuid primary key default gen_random_uuid(),
        worker_id text unique not null,
        status text default 'offline',
        last_heartbeat timestamp with time zone default now()
    );
    """,
    """
    create table if not exists public.call_transcripts (
        id uuid primary key default gen_random_uuid(),
        call_id text unique,
        assistant_id text,
        phone_number text,
        transcript text,
        summary text,
        sentiment text, -- 'positive', 'neutral', 'negative'
        metadata jsonb default '{}'::jsonb,
        created_at timestamp with time zone default now()
    );
    """,
    """
    alter table public.call_transcripts enable row level security;
    """,
    """
    create policy "Enable all access for service role and anon" on public.call_transcripts for all using (true) with check (true);
    """,
    """
    create table if not exists public.api_cache (
        key text primary key,
        value jsonb,
        created_at timestamp with time zone default now()
    );
    """,
    """
    alter table public.api_cache enable row level security;
    """,
    """
    create policy "Enable all access for service role and anon" on public.api_cache for all using (true) with check (true);
    """,
    """
    create table if not exists public.system_logs (
        id uuid primary key default gen_random_uuid(),
        worker_id text,
        level text, -- 'INFO', 'ERROR', 'WARNING'
        message text,
        context jsonb default '{}'::jsonb,
        created_at timestamp with time zone default now()
    );
    """,
    """
    alter table public.system_logs enable row level security;
    """,
    """
    create policy "Enable insert for service role and anon" on public.system_logs for insert with check (true);
    """,
    """
    create policy "Enable select for service role and anon" on public.system_logs for select using (true);
    """,
    """
    alter table public.tasks_queue enable row level security;
    """,
    """
    alter table public.agent_presence enable row level security;
    """,
    # RLS Policies (Idempotent-ish checks slightly harder in raw SQL without DO block, trying simplistic creation)
    # We will wrap in try/except in python loop
    """
    create policy "Enable all access for service role" on public.tasks_queue for all using (true) with check (true);
    """,
    """
    create policy "Enable all access for anon" on public.tasks_queue for all to anon using (true) with check (true);
    """,
     """
    create policy "Enable all access for service role" on public.agent_presence for all using (true) with check (true);
    """,
    # Realtime
    """
    alter publication supabase_realtime add table public.tasks_queue;
    """,
     """
    alter publication supabase_realtime add table public.agent_presence;
    """
]

def apply():
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        print("✅ Connected to Database.")
        
        for sql in sql_commands:
            try:
                cur.execute(sql)
                print("   Executed SQL chunk.")
            except Exception as e:
                print(f"   ⚠️ SQL Warning/Skipped: {e}")
                # likely "already exists" or similar
                
        print("✅ Schema patch applied.")
        
        # Verification
        cur.execute("SELECT to_regclass('public.tasks_queue');")
        exists = cur.fetchone()[0]
        print(f"VERIFY: Table 'public.tasks_queue' exists? {exists}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Database Connection Failed: {e}")

if __name__ == "__main__":
    apply()
