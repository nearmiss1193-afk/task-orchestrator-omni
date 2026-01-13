import os
import sqlite3
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_learning_status():
    print("\n🧠 OPTIMIZED LEARNING SYSTEM CHECK")
    print("=" * 40)

    # 1. Config Check
    rl_enabled = os.getenv("RL_TRAINING_ENABLED", "false")
    print(f"Config: RL_TRAINING_ENABLED = {rl_enabled}")
    
    # 2. Module Check
    modules = ["modules/rl_trainer.py", "modules/meta_learner.py", "modules/graph_store.py"]
    print("\n📦 Modules:")
    for mod in modules:
        exists = os.path.exists(mod)
        print(f"  - {mod}: {'✅ Found' if exists else '❌ Missing'}")

    # 3. Knowledge Graph (Local SQLite)
    print("\n🕸️  Knowledge Graph (Local):")
    if os.path.exists("graph_store.db"):
        try:
            conn = sqlite3.connect("graph_store.db")
            cursor = conn.cursor()
            count = cursor.execute("SELECT count(*) FROM nodes").fetchone()[0]
            print(f"  - Status: ✅ Active")
            print(f"  - Nodes: {count}")
            conn.close()
        except Exception as e:
            print(f"  - Status: ⚠️ Error reading DB: {e}")
    else:
        print("  - Status: ❌ Database file not found (graph_store.db)")

    # 4. Agent Learnings (Supabase)
    print("\n💾 Agent Learnings (Central):")
    try:
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        client = create_client(url, key)
        
        # Check 'agent_learnings' table
        learnings = client.table("agent_learnings").select("*", count="exact").execute()
        count = learnings.count
        print(f"  - Total Learning Records: {count}")
        
        if count > 0:
            latest = client.table("agent_learnings").select("created_at, category, insight").order("created_at", desc=True).limit(1).execute()
            if latest.data:
                l = latest.data[0]
                print(f"  - Latest Insight ({l['created_at'][:16]}): [{l['category']}] {l['insight'][:50]}...")
        else:
            print("  - ⚠️ No learnings recorded yet (System might be too new or no errors triggered)")

    except Exception as e:
        print(f"  - Status: ❌ Error connecting to Supabase: {e}")

if __name__ == "__main__":
    check_learning_status()
