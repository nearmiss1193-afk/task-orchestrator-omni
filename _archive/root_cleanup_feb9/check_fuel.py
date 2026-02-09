import os
import requests
import json
from dotenv import load_dotenv

# Hardcode or load from local .env if possible, but I'll try to reach out to the DB
load_dotenv()

url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("❌ Missing Supabase Credentials in environment")
    exit(1)

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

def get_count(status):
    # Select count via REST API
    query_url = f"{url}/rest/v1/contacts_master?status=eq.{status}&select=id"
    res = requests.get(query_url, headers={**headers, "Prefer": "count=exact"})
    range_header = res.headers.get("Content-Range")
    if range_header:
        return range_header.split("/")[-1]
    return "0"

def get_total():
    query_url = f"{url}/rest/v1/contacts_master?select=id"
    res = requests.get(query_url, headers={**headers, "Prefer": "count=exact"})
    range_header = res.headers.get("Content-Range")
    if range_header:
        return range_header.split("/")[-1]
    return "0"

print("--- Supabase Lead Fuel Audit ---")
print(f"Total Leads: {get_total()}")
for s in ["new", "research_done", "outreach_sent", "calling_initiated", "trash", "call_interested", "call_booked"]:
    print(f"Status '{s}': {get_count(s)}")
