import os
import json
from dotenv import load_dotenv
load_dotenv(r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

from supabase import create_client

url = "https://rzcpfwkygdvoshtwxncs.supabase.co"
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

c = create_client(url, key)

# Get contacts with websites (any status)
with_website = c.table("contacts_master").select("id,company_name,full_name,website_url,email,status,phone,niche").not_.is_("website_url","null").not_.eq("website_url","").limit(15).execute()

print(f"Found {len(with_website.data)} contacts with websites")

prospects = []
for p in with_website.data:
    prospects.append({
        "id": p.get("id"),
        "company_name": p.get("company_name") or p.get("full_name","Unknown"),
        "contact_name": p.get("full_name","Business Owner"),
        "email": p.get("email"),
        "website": p.get("website_url"),
        "phone": p.get("phone"),
        "status": p.get("status"),
        "niche": p.get("niche")
    })
    print(f"  {p.get('company_name') or p.get('full_name','?')}: {p.get('website_url')} [{p.get('status')}]")

# Save for PageSpeed testing
with open("prospects_for_pagespeed.json", "w") as f:
    json.dump(prospects[:10], f, indent=2)
print(f"\nSaved {min(10, len(prospects))} prospects to prospects_for_pagespeed.json")
