import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def setup_learnings_table():
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("❌ Missing credentials")
        return

    # We can't run DDL (CREATE TABLE) directly via supabase-py client easily unless we use SQL functionality 
    # if enabled or via dashboard.
    # However, we can try to use a raw RPC call if a function exists, or just tell the user.
    # BUT, wait, I can use the 'postgres' connection if I had the connection string, but I only have the API URL/Key.
    
    # Alternative: The user might have a 'setup_db.py' or similar I can leverage, 
    # or I might have to instruct the user to run SQL.
    # Actually, let's try to see if we can use the 'rpc' method if there's an 'exec_sql' function, 
    # but standard Supabase doesn't expose that by default.
    
    # STRATEGY CHANGE: I will assume I cannot create tables via Client API directly without an RPC wrapper.
    # I will check if I can use the `modal_deploy.py` or `continuous_swarm.py` to initialize it? 
    # No, usually I need SQL.
    
    # Let's verify if the Error was actually "Table not found".
    client = create_client(url, key)
    
    print("Checking 'agent_learnings' table...")
    try:
        # Try a simple select
        client.table("agent_learnings").select("*").limit(1).execute()
        print("✅ Table 'agent_learnings' exists.")
    except Exception as e:
        print(f"❌ Table check failed: {e}")
        print("\n⚠️ ACTION REQUIRED: Run this SQL in your Supabase Dashboard SQL Editor:")
        print("-" * 50)
        print("""
CREATE TABLE IF NOT EXISTS agent_learnings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    category TEXT NOT NULL,
    insight TEXT NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    source TEXT,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_agent_learnings_category ON agent_learnings(category);
        """)
        print("-" * 50)

if __name__ == "__main__":
    setup_learnings_table()
