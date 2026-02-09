import os
from dotenv import load_dotenv

load_dotenv()
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env", override=True)

url = os.environ.get("DATABASE_URL")
if url:
    print(f"DATABASE_URL found. Length: {len(url)}")
    print(f"Prefix: {url[:20]}")
    print(f"Contains password: {'Yes' if ':' in url.split('@')[0][13:] else 'No'}")
else:
    print("DATABASE_URL NOT FOUND")

key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
if key:
    print(f"SUPABASE_SERVICE_ROLE_KEY found. Length: {len(key)}")
else:
    print("SUPABASE_SERVICE_ROLE_KEY NOT FOUND")
