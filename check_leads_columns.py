import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
}

res = requests.get(f"{url}/rest/v1/leads?limit=1", headers=headers)
if res.status_code == 200:
    data = res.json()
    if data:
        for k in sorted(data[0].keys()):
            print(f"COLUMN: {k}")
    else:
        print("EMPTY")
else:
    print("FAIL")
