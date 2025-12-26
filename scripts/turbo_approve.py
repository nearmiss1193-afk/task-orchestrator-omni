
import os
import requests
import json
from datetime import datetime
from supabase import create_client, Client

# Load environment variables manually if needed, or use os.environ
# Assuming they are set in the environment or we can read from .env.local
def load_env():
    env_path = ".env.local"
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value

load_env()

SUB_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
GHL_TOKEN = os.environ.get("GHL_API_TOKEN") or os.environ.get("GHL_PRIVATE_KEY")

def get_supabase() -> Client:
    return create_client(SUB_URL, SUB_KEY)

def approve_all():
    print("🚀 Starting Python Turbo Approval Loop...")
    
    supabase = get_supabase()
    
    # 1. Fetch pending replies
    try:
        response = supabase.table("staged_replies").select("*").eq("status", "pending_approval").execute()
        pending = response.data
    except Exception as e:
        print(f"❌ Error fetching from Supabase: {str(e)}")
        return

    if not pending:
        print("✅ No replies pending approval.")
        return

    print(f"📝 Found {len(pending)} replies to approve.")

    for reply in pending:
        cid = reply.get("contact_id")
        rid = reply.get("id")
        content = reply.get("draft_content")
        platform = reply.get("platform") or "sms"
        
        print(f"📤 Sending reply to contact {cid}...")
        
        # 2. Dispatch via GHL
        ghl_url = "https://services.leadconnectorhq.com/conversations/messages"
        headers = {
            "Authorization": f"Bearer {GHL_TOKEN}",
            "Version": "2021-04-15",
            "Content-Type": "application/json"
        }
        payload = {
            "type": platform,
            "contactId": cid,
            "body": content
        }
        
        try:
            res = requests.post(ghl_url, json=payload, headers=headers)
            if res.status_code in [200, 201]:
                print(f"✅ Sent successfully to {cid}")
                # 3. Update status
                supabase.table("staged_replies").update({
                    "status": "sent",
                    "sent_at": datetime.now().isoformat()
                }).eq("id", rid).execute()
            else:
                print(f"⚠️ Failed to send to {cid}: {res.text}")
        except Exception as e:
            print(f"❌ Error processing {cid}: {str(e)}")

    print("🏁 Python Turbo Approval Complete.")

if __name__ == "__main__":
    approve_all()
