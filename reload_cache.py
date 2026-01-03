
import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.environ["NEXT_PUBLIC_SUPABASE_URL"]
key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Sometimes simply making a request to the root API can trigger a refresh check or wake it up
print(f"Pinging Supabase API at {url}...")
try:
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    # Try to access the new table directly via REST to force it into the cache
    res = requests.get(f"{url}/rest/v1/brain_logs?select=*", headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text[:200]}")
    
    if res.status_code == 200:
        print("Schema Cache Refreshed! Table is accessible.")
    else:
        print("Table still not found via REST API.")

except Exception as e:
    print(f"Error: {e}")
