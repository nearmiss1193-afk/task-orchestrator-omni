
import modal
import deploy
import json

app = deploy.app

@app.local_entrypoint()
def main():
    print("🔮 Checking Database Health...")
    check_db.remote()

@app.function(image=deploy.image, secrets=[deploy.VAULT])
def check_db():
    supabase = deploy.get_supabase()
    
    # 1. Check Brain Logs (Should exist)
    try:
        res = supabase.table("brain_logs").select("*").limit(1).execute()
        print(f"✅ brain_logs access OK. Rows: {len(res.data)}")
    except Exception as e:
        print(f"❌ brain_logs Error: {e}")

    # 2. Check Contacts Master
    try:
        res = supabase.table("contacts_master").select("*").limit(1).execute()
        print(f"✅ contacts_master access OK. Rows: {len(res.data)}")
    except Exception as e:
        print(f"❌ contacts_master Error: {e}")
        # If does not exist, we should probably output the SQL needed.
