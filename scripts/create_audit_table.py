"""Create the audit_reports table via Supabase's postgrest-js rpc or direct SQL"""
import os, requests

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://rzcpfwkygdvoshtwxncs.supabase.co')
SUPABASE_KEY = os.environ['SUPABASE_KEY']

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# Try to create table using SQL via REST
# First try the rpc endpoint
sql = """
CREATE TABLE IF NOT EXISTS audit_reports (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    report_id text UNIQUE NOT NULL,
    lead_id text,
    company_name text,
    website_url text,
    audit_results jsonb,
    pdf_url text,
    created_at timestamptz DEFAULT now(),
    viewed_at timestamptz,
    view_count int DEFAULT 0
);
"""

# Method 1: Try RPC
print("Trying RPC method...")
r = requests.post(
    f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
    headers=headers,
    json={"query": sql}
)
print(f"RPC result: {r.status_code} - {r.text[:200]}")

# Method 2: Check if table already exists by trying to select
print("\nChecking if table exists via REST select...")
r2 = requests.get(
    f"{SUPABASE_URL}/rest/v1/audit_reports?select=id&limit=1",
    headers=headers
)
print(f"Select result: {r2.status_code} - {r2.text[:200]}")

if r2.status_code == 200:
    print("\n✅ Table exists! (or was just created)")
elif r2.status_code == 404 or '42P01' in r2.text:
    print("\n❌ Table does NOT exist yet.")
    print("You need to run this SQL in the Supabase dashboard SQL editor:")
    print("Go to: https://supabase.com/dashboard/project/rzcpfwkygdvoshtwxncs/sql/new")
    print(sql)
    print("""
-- Also run:
ALTER TABLE audit_reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read" ON audit_reports FOR SELECT USING (true);
CREATE POLICY "Allow service role insert" ON audit_reports FOR INSERT WITH CHECK (true);
CREATE INDEX IF NOT EXISTS idx_audit_reports_report_id ON audit_reports(report_id);
""")
else:
    print(f"\nUnexpected response: {r2.status_code}")
