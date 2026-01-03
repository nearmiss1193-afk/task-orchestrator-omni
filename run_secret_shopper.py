
import os
import sys
from modules.testing.secret_shopper import SecretShopper
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Load Env
url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Missing Supabase Credentials")
    sys.exit(1)

supabase = create_client(url, key)

print("🚀 Launching Manual Secret Shopper (Turbo Mode)...")
webhook_url = "https://nearmiss1193-afk--ghl-omni-automation-ghl-webhook.modal.run"
shopper = SecretShopper(supabase, webhook_url=webhook_url)
result = shopper.execute_shop()

print(f"\n📝 Result: {result}")
