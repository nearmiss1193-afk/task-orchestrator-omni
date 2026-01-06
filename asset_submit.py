import os
import argparse
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

def submit_asset(asset_type, url, category=None, metadata=None):
    data = {
        "type": asset_type,
        "url": url,
        "category": category or "other",
        "metadata": metadata or {}
    }
    
    try:
        response = supabase.table("asset_inbox").insert(data).execute()
        print(f"✅ Asset submitted successfully: {asset_type} | {url}")
        return response.data
    except Exception as e:
        print(f"❌ Submission failed: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Asset Submission Tool")
    parser.add_argument("--type", required=True, choices=["video", "link", "image", "document"], help="Type of asset")
    parser.add_argument("--url", required=True, help="URL of the asset")
    parser.add_argument("--category", help="Optional category (email, marketing, etc.)")
    parser.add_argument("--meta", help="Optional JSON metadata string")

    args = parser.parse_args()
    
    metadata = {}
    if args.meta:
        try:
            metadata = json.loads(args.meta)
        except:
            print("⚠️ Invalid metadata JSON. Using empty dict.")

    submit_asset(args.type, args.url, args.category, metadata)
