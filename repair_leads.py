import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
client = create_client(url, key)

sql_statements = [
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS phone TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS city TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS state TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS industry TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS website TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_called TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_contact_at TIMESTAMP WITH TIME ZONE;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS agent_research JSONB DEFAULT '{}'::jsonb;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS personalized_copy TEXT;",
    "ALTER TABLE leads ADD COLUMN IF NOT EXISTS ghl_contact_id TEXT;"
]

def run_migration():
    print("🚀 Starting Lead Table Repair...")
    for sql in sql_statements:
        try:
            # We use RPC exec_sql which is standard in these Empire templates
            client.rpc('exec_sql', {'sql': sql}).execute()
            print(f"✅ Executed: {sql[:30]}...")
        except Exception as e:
            print(f"❌ Failed: {sql[:30]}... Error: {e}")

if __name__ == "__main__":
    run_migration()
