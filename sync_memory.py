
import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Supabase credentials missing.")
    exit()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def sync_memory():
    memory_file = "knowledge_base/operational_memory.md"
    if not os.path.exists(memory_file):
        print(f"❌ File not found: {memory_file}")
        return

    with open(memory_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"🧠 Syncing {len(content)} bytes of operational memory...")

    # Table: system_memory (key, value, last_updated)
    data = {
        "key": "operational_buffer",
        "value": content,
        "last_updated": time.strftime('%Y-%m-%d %H:%M:%S%z')
    }

    # Upsert logic (delete/insert or upsert if supported)
    # Supabase upsert requires a unique constraint on 'key', which we defined in SQL
    
    try:
        supabase.table('system_memory').upsert(data, on_conflict='key').execute()
        print("✅ Memory synced successfully.")
    except Exception as e:
        print(f"❌ Error syncing memory: {e}")

if __name__ == "__main__":
    sync_memory()
