import os
from dotenv import load_dotenv

env_path = os.path.join(os.getcwd(), ".env")
print(f"Checking .env at: {env_path}")

if os.path.exists(env_path):
    print("✅ .env file found.")
    with open(env_path, 'r') as f:
        content = f.read()
        print(f"File size: {len(content)} bytes")
        if "SUPABASE_URL" in content:
            print("✅ SUPABASE_URL string found in file content.")
        else:
            print("❌ SUPABASE_URL NOT found in file content.")
else:
    print("❌ .env file NOT found.")

load_dotenv(env_path)
url = os.getenv("SUPABASE_URL")
if url:
    print(f"✅ Loaded SUPABASE_URL: {url[:10]}...")
else:
    print("❌ Failed to load SUPABASE_URL into os.environ")
