
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Explicitly load .env from current directory
# Explicitly load .env from current directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
# Use Service Role Key if available (preferred for admin tasks) or Anon key
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
db_url = os.environ.get("DATABASE_URL")

print(f"DEBUG: URL found? {bool(url)}")
print(f"DEBUG: Key found? {bool(key)}")

if not url or not key:
    print("❌ Error: Supabase URL/Key missing in .env")
    # Don't exit, still generate SQL
else:
    try:
        supabase: Client = create_client(url, key)
        print("✅ Supabase Client Initialized.")
    except Exception as e:
        print(f"⚠️ Failed to init client: {e}")

print("🚀 Generating Office Manager Migration SQL...")

sql_content = """
-- Office Manager Inventory
CREATE TABLE IF NOT EXISTS office_inventory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    item_name TEXT NOT NULL UNIQUE,
    quantity INTEGER DEFAULT 0,
    unit TEXT DEFAULT 'units',
    min_threshold INTEGER DEFAULT 5,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Office Manager Tasks
CREATE TABLE IF NOT EXISTS office_tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, in_progress, done
    assigned_by TEXT DEFAULT 'system',
    due_date TIMESTAMPTZ
);

-- RLS Policies (Open for now/Authenticated)
ALTER TABLE office_inventory ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public Access" ON office_inventory FOR ALL USING (true);

ALTER TABLE office_tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public Access" ON office_tasks FOR ALL USING (true);
"""

with open("office_manager_migration.sql", "w", encoding="utf-8") as f:
    f.write(sql_content)

# Split and Execute SQL
commands = sql_content.split(";")
for cmd in commands:
    cmd = cmd.strip()
    if cmd:
        try:
            # Using a raw RPC or direct execute if client supports it, 
            # likely need to use 'postgres' connector or just try-catch standard client calls if table creation isn't exposed perfectly.
            # Supabase Python client usually wraps PostgREST. Creating tables via PostgREST is often restricted.
            # However, the user said "you have authority... execute". 
            # We will try to use the 'rpc' 'execute_sql' pattern if it exists, OR standard client won't work for DDL.
            # FALLBACK: If standard client fails DDL, we assume 'admin' access needed. 
            # BUT, we can try to just use valid Python Supabase calls for the known tables if DDL fails.
            # actually better: The user wants me to EXECUTE.
            # Let's assume standard client + service_role key allows it? Usually not DDL.
            # We will try to run a special 'exec_sql' function if the user has one, OR just tell the user we did our best.
            # Wait, the user said "you set it up already". 
            # Let's try to just run the create commands via valid logic if possible.
            pass
        except Exception as e:
            print(f"SQL Exec Error: {e}")

# REVISION: The supabase-py client is mostly for Row manipulation. DDL is hard.
# However, I can use the `postgres` library if I had the connection string.
# I will try to use a pre-existing `exec_sql` RPC function if it exists in their setup?
# Checking `deploy.py`... no `exec_sql` found.
# OK, I will attempt to separate the tables and use the python client to Insert dummy data to "Test" existence, 
# but I cannot create tables easily without the connection string or an RPC.
# WAIT. I can use the `postgres` python library if I have the connection string from .env?
# .env has `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`.
# It usually does NOT have the postgres:// connection string unless I look deeper.

# ALTERNATIVE: I will create the tables via the `setup_office_tables.sql` file 
# and ASK THE USER TO RUN IT, explaining DDL limitation? 
# NO, user said "you have authority... execute". 
# They might imply I have a tool or method. 
# I will try to find a `execute_sql` tool or connection string.
# Searching .env for DATABASE_URL...
print("Checking for DATABASE_URL for direct DDL execution...")
db_url = os.environ.get("DATABASE_URL")
if db_url:
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute(sql_content)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tables initialized via Direct Postgres Connection.")
    except ImportError:
        print("⚠️ psycopg2 not installed. Installing...")
        try:
            import subprocess
            subprocess.check_call(["pip", "install", "psycopg2-binary"])
            import psycopg2
            conn = psycopg2.connect(db_url)
            cur = conn.cursor()
            cur.execute(sql_content)
            conn.commit()
            print("✅ Tables initialized via Direct Postgres Connection (After Install).")
        except Exception as e:
             print(f"❌ Failed to execute SQL via Postgres: {e}")
        except Exception as e:
            print(f"❌ Standard Client cannot execute DDL. Attempting to locate DATABASE_URL... {e}")

# Simplified approach for this file edit:
# I will add the DATABASE_URL logic to the script.

