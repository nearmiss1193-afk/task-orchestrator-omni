"""
ANTIGRAVITY v6.0 — Income Pipeline Check
Run this at the START of every session per the Revenue-Verified Autonomy protocol.
"""
import os, json
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

url = os.environ.get("SUPABASE_URL", "https://rzcpfwkygdvoshtwxncs.supabase.co")
key = os.environ.get("SUPABASE_KEY", "")

sb = create_client(url, key)

print("=" * 50)
print("INCOME PIPELINE CHECK — v6.0 Protocol")
print("=" * 50)

# Step 1: SENDING?
try:
    r = sb.rpc('', {}).execute()  # fallback to direct query
except:
    pass

try:
    r = sb.table("outbound_touches").select("id", count="exact").gte("ts", "now() - interval '24 hours'").execute()
    print(f"\n1. SENDING:   {r.count or len(r.data)} touches in last 24h")
except Exception as e:
    # Try raw approach
    r = sb.table("outbound_touches").select("id,ts").order("ts", desc=True).limit(10).execute()
    recent = r.data if r.data else []
    print(f"\n1. SENDING:   {len(recent)} most recent touches")
    if recent:
        print(f"   Last touch: {recent[0].get('ts', 'unknown')}")
    else:
        print(f"   !! ZERO TOUCHES FOUND !!")

# Step 2: Check for opens/replies (column may not exist)
try:
    r = sb.table("outbound_touches").select("id,channel,ts,status").order("ts", desc=True).limit(20).execute()
    data = r.data or []
    channels = {}
    for d in data:
        ch = d.get('channel', 'unknown')
        channels[ch] = channels.get(ch, 0) + 1
    print(f"\n2. CHANNELS:  {json.dumps(channels)}")
    if data:
        print(f"   Latest:    {data[0].get('ts', '?')} via {data[0].get('channel', '?')}")
except Exception as e:
    print(f"\n2. CHANNELS:  Error - {e}")

# Step 3: Pipeline health
try:
    r = sb.table("contacts_master").select("status", count="exact").execute()
    statuses = {}
    for row in (r.data or []):
        s = row.get('status', 'unknown')
        statuses[s] = statuses.get(s, 0) + 1
    print(f"\n3. PIPELINE:  {json.dumps(statuses)}")
    contactable = statuses.get('new', 0) + statuses.get('research_done', 0)
    print(f"   Contactable leads: {contactable}")
except Exception as e:
    print(f"\n3. PIPELINE:  Error - {e}")

# Step 4: Campaign mode
try:
    r = sb.table("system_state").select("*").eq("key", "campaign_mode").execute()
    if r.data:
        print(f"\n4. CAMPAIGN:  {r.data[0].get('status', 'unknown')}")
    else:
        print(f"\n4. CAMPAIGN:  No campaign_mode row found")
except Exception as e:
    print(f"\n4. CAMPAIGN:  Error - {e}")

# Step 5: Heartbeat
try:
    r = sb.table("system_health_log").select("checked_at,status").order("checked_at", desc=True).limit(1).execute()
    if r.data:
        print(f"\n5. HEARTBEAT: {r.data[0].get('checked_at', '?')} — {r.data[0].get('status', '?')}")
    else:
        print(f"\n5. HEARTBEAT: No heartbeat found")
except Exception as e:
    print(f"\n5. HEARTBEAT: Error - {e}")

print(f"\n{'=' * 50}")
print("END PIPELINE CHECK")
print("=" * 50)
