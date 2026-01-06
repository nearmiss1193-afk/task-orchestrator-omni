import os
import time
import json
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not URL or not KEY:
    print("❌ Supabase credentials missing in .env")
    exit(1)

supabase: Client = create_client(URL, KEY)

def process_assets():
    print("👀 Antigravity Watchdog: Scanning Asset Inbox...")
    
    try:
        # Get pending assets
        res = supabase.table("asset_inbox").select("*").eq("status", "pending").execute()
        assets = res.data
        
        if not assets:
            print("😴 No pending assets.")
            return

        for asset in assets:
            asset_id = asset['id']
            asset_type = asset['type']
            url = asset['url']
            
            print(f"🔄 Processing {asset_type}: {url}...")
            
            # Initial categorization logic (Simulated for now, can be expanded with AI)
            status = "completed"
            category = asset.get('category', 'other')
            
            if "trash" in url.lower() or "spam" in url.lower():
                status = "trash"
                print(f"🗑️ Asset marked as TRASH.")
            elif "email" in url.lower() or "newsletter" in url.lower():
                category = "email"
                print(f"✉️ Routing to OUTGOING EMAIL sequence.")
            else:
                print(f"📁 Asset categorized as {category.upper()}.")

            # Update status
            supabase.table("asset_inbox").update({
                "status": status,
                "category": category,
                "updated_at": "now()"
            }).eq("id", asset_id).execute()
            
            print(f"✅ {asset_id} marked as {status}.")

    except Exception as e:
        print(f"❌ Watchdog Error: {e}")

if __name__ == "__main__":
    while True:
        process_assets()
        time.sleep(30) # Scan every 30 seconds
