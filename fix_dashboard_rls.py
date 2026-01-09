"""
Fix Dashboard RLS - Disable RLS to allow anon access
"""
import psycopg2

conn = psycopg2.connect('postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres')
cur = conn.cursor()

print("="*50)
print("FIXING RLS FOR DASHBOARD")
print("="*50)

# Disable RLS completely on dashboard tables
tables = ['leads', 'call_transcripts', 'system_logs']

for table in tables:
    try:
        cur.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
        print(f"Disabled RLS on {table}")
    except Exception as e:
        print(f"Error {table}: {e}")

conn.commit()

# Verify counts work
for table in tables:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    print(f"  {table}: {count} rows")

conn.close()
print("="*50)
print("DONE! Refresh dashboard now.")
