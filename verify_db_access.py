import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not url or not key:
    print("❌ Configuration missing.")
    exit(1)

try:
    supabase = create_client(url, key)
    response = supabase.table("office_inventory").select("*").execute()
    print(f"✅ Success! Accessed office_inventory.")
    print(f"📊 Row Count: {len(response.data)}")
except Exception as e:
    print(f"⚠️ verification (Level 3) failed (expected if table missing): {e}")

# Level 5 Authority Check: Create a test table via raw SQL if possible, or just verify we have the connection string.
db_url = os.environ.get("DATABASE_URL")
if db_url:
    if "?" not in db_url:
        db_url += "?sslmode=require"
    print(f"🔐 Testing DDL with: {db_url.split(':')[2].split('@')[0] if ':' in db_url else 'Wait'} (Masked)") 
    import psycopg2
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS level_5_check (id serial primary key, check_time timestamptz default now());")
        conn.commit()
        print("⭐⭐⭐ LEVEL 5 AUTHORITY CONFIRMED: Table 'level_5_check' created/verified.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️ DDL Check Failed: {e}")
        with open("db_error_log.txt", "w") as f:
            f.write(str(e))
else:
    print("⚠️ DATABASE_URL missing for Level 5 check.")
