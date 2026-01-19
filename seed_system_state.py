#!/usr/bin/env python3
"""Seed system_state table via direct REST API calls"""
import requests

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

# Default system state values
defaults = [
    {"key": "CAMPAIGN_MODE", "value": '"RUN"', "updated_by": "migration"},
    {"key": "OUTREACH_ENABLED", "value": "true", "updated_by": "migration"},
    {"key": "SMS_ENABLED", "value": "true", "updated_by": "migration"},
    {"key": "EMAIL_ENABLED", "value": "true", "updated_by": "migration"},
    {"key": "CALLS_ENABLED", "value": "true", "updated_by": "migration"},
    {"key": "MAX_BATCH_SIZE", "value": "25", "updated_by": "migration"},
    {"key": "RATE_LIMITS", "value": '{"sms_per_hour": 60, "email_per_hour": 30, "calls_per_hour": 15}', "updated_by": "migration"},
    {"key": "NEXT_ACTIONS", "value": '{}', "updated_by": "migration"},
    {"key": "LAUNCH_MODE", "value": '"BUSINESS_HOURS"', "updated_by": "migration"}
]

print("Seeding system_state table...")

for item in defaults:
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/system_state",
        headers=headers,
        json=item
    )
    status = "✓" if r.status_code < 300 else f"✗ {r.status_code}"
    print(f"  {status} {item['key']}")

# Verify
print("\nVerifying system_state:")
r = requests.get(f"{SUPABASE_URL}/rest/v1/system_state?select=key,value", headers=headers)
if r.ok:
    for item in r.json():
        print(f"  {item['key']}: {item['value']}")
else:
    print(f"  Table may not exist yet: {r.status_code}")
    print("  Run this SQL in Supabase dashboard:")
    print("""
    CREATE TABLE IF NOT EXISTS system_state (
        key TEXT PRIMARY KEY,
        value JSONB NOT NULL,
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        updated_by TEXT DEFAULT 'system'
    );
    """)
