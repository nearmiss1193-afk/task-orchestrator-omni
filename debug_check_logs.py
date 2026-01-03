
import os
import modal
import sys

# Load Envs
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

import supabase

def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        print("Missing Supabase Credentials")
        return None
    return supabase.create_client(url, key)

def check_logs():
    db = get_supabase()
    if not db:
        return

    print("--- FETCHING RECENT BRAIN LOGS ---")
    try:
        # Fetch last 20 logs
        res = db.table("brain_logs").select("*").order("created_at", desc=True).limit(20).execute()
        for log in res.data:
            print(f"[{log.get('created_at')}] {log.get('level')}: {log.get('message')}")
            
    except Exception as e:
        print(f"Error fetching logs: {e}")


if __name__ == "__main__":
    # Local check failed due to missing envs.
    # We will just print instructions to run on Modal.
    print("Please run this via Modal: python -m modal run debug_check_logs.py")



import dotenv
dotenv.load_dotenv()
import os
import modal

app = modal.App("debug_logs")
image = modal.Image.debian_slim().pip_install("supabase", "python-dotenv")

VAULT = modal.Secret.from_dict({
    "SUPABASE_URL": os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL"),
    "SUPABASE_SERVICE_ROLE_KEY": os.environ.get("SUPABASE_SERVICE_ROLE_KEY"),
    "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
    "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
    "GHL_AGENCY_API_TOKEN": os.environ.get("GHL_AGENCY_API_TOKEN"),
    "GHL_LOCATION_ID": os.environ.get("GHL_LOCATION_ID"),
})


@app.function(image=image, secrets=[VAULT])
def check_logs_cloud():
    print("--- FETCHING RECENT BRAIN LOGS (CLOUD) ---")
    try:
        import os
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            print("Missing Credentials in Cloud")
            return
            
        client = supabase.create_client(url, key)
        # Fetch logs from last 15 minutes
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        since = now - datetime.timedelta(minutes=15)
        
        res = client.table("brain_logs").select("*").gt("created_at", since.isoformat()).order("created_at", desc=True).limit(50).execute()
        for log in res.data:
            print(f"[{log.get('created_at')}] {log.get('level')}: {log.get('message')}")
            
    except Exception as e:
        print(f"Error fetching logs: {e}")

@app.local_entrypoint()
def main():
    check_logs_cloud.remote()

