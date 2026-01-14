"""Check if source column exists and look for railway leads"""
from dotenv import load_dotenv
load_dotenv('backups/empire_backup_20260108_182239/source/.env')
import os
import requests

url = os.environ.get('NEXT_PUBLIC_SUPABASE_URL')
key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

# Try to get leads with source column
print("Checking for source column...")
r = requests.get(
    f'{url}/rest/v1/leads',
    params={'select': 'id,company_name,status,source,created_at', 'limit': 5},
    headers={'apikey': key, 'Authorization': f'Bearer {key}'}
)
print(f"Status: {r.status_code}")
if r.ok:
    for l in r.json():
        print(f"  - {l}")
else:
    print(r.text)

# Count total leads
print("\nTotal leads count:")
r2 = requests.get(
    f'{url}/rest/v1/leads',
    params={'select': 'id'},
    headers={'apikey': key, 'Authorization': f'Bearer {key}', 'Prefer': 'count=exact'}
)
print(f"Content-Range: {r2.headers.get('Content-Range', 'N/A')}")
