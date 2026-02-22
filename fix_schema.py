import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# We use the DATABASE_URL to connect to Neon directly to run DDL (Data Definition Language)
# since Supabase REST API does not allow CREATE TABLE
db_url = os.environ.get("DATABASE_URL")

if not db_url:
    print("❌ Critical: DATABASE_URL not found in environment.")
    exit(1)

try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS system_error_log (
        id BIGSERIAL PRIMARY KEY,
        source TEXT,
        error_type TEXT,
        error_message TEXT,
        traceback TEXT,
        status TEXT,
        retry_count INTEGER,
        context JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    
    cursor.execute(query)
    print("✅ Successfully created `system_error_log` table in Supabase/Neon.")

    # Also make sure RLS is disabled or appropriate policies exist so REST can insert
    # We will disable RLS for this internal system table to ensure logging never fails
    rls_query = "ALTER TABLE system_error_log DISABLE ROW LEVEL SECURITY;"
    cursor.execute(rls_query)
    print("✅ Disabled RLS on `system_error_log` for seamless insertion.")

except Exception as e:
    print(f"❌ Failed to create table: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
