import os
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(".env")

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def probe():
    if not url or not key:
        print("❌ No Supabase URL/Key")
        return

    supabase: Client = create_client(url, key)
    
    # Common names for SQL exec functions
    # exec, exec_sql, execute, query, run_sql
    targets = ["exec", "exec_sql", "execute_sql", "run_sql", "query"]
    
    print("🕵️ Probing RPCs...")
    
    for t in targets:
        try:
            # Try to run 'SELECT 1'
            res = supabase.rpc(t, {"query": "SELECT 1"}).execute()
            print(f"✅ FOUND RPC: {t} -> {res.data}")
            return t
        except Exception as e:
            # print(f"   {t} failed: {e}") 
            # Often 404/Function not found
            pass
            
        try:
            # Try with 'sql' param
            res = supabase.rpc(t, {"sql": "SELECT 1"}).execute()
            print(f"✅ FOUND RPC: {t} (sql param) -> {res.data}")
            return t
        except:
            pass
            
    print("❌ No SQL Execution RPC found.")
    return None

if __name__ == "__main__":
    probe()
