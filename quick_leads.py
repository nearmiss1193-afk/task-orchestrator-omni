#!/usr/bin/env python3
"""Quick lead pull for immediate outreach."""
import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL or SUPABASE_KEY not set")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get 15 contacts with phones
result = supabase.table("contacts_master").select(
    "id,first_name,last_name,company,phone,email,status"
).not_.is_("phone", "null").limit(15).execute()

print(f"Found {len(result.data)} contacts with phones:")
for i, c in enumerate(result.data[:15], 1):
    print(f"{i}. {c.get('first_name')} {c.get('last_name')} - {c.get('company')} - {c.get('phone')} [{c.get('status')}]")

if len(result.data) > 0:
    print(f"\nReady for outreach: {len(result.data)} leads")
else:
    print("\nNo leads found with phone numbers in contacts_master")
