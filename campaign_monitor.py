"""
OUTREACH CAMPAIGN MONITOR - Check status of leads, interactions, and campaign health
"""
import requests
from collections import Counter
from datetime import datetime

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
headers = {"apikey": SUPABASE_KEY}

def monitor():
    print("=" * 60)
    print(f"OUTREACH CAMPAIGN MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Lead status breakdown
    r = requests.get(f"{SUPABASE_URL}/rest/v1/leads?select=status,industry&limit=500", headers=headers)
    leads = r.json() if r.status_code == 200 else []
    statuses = Counter([l.get("status") for l in leads])
    industries = Counter([l.get("industry") for l in leads])

    print(f"\n[LEADS] Total: {len(leads)}")
    for s, c in statuses.most_common():
        print(f"  {s}: {c}")

    print(f"\n[INDUSTRIES]")
    for i, c in industries.most_common(5):
        print(f"  {i}: {c}")

    # Recent interactions
    r2 = requests.get(f"{SUPABASE_URL}/rest/v1/interactions?select=id,created_at,intent,outcome&order=created_at.desc&limit=10", headers=headers)
    interactions = r2.json() if r2.status_code == 200 else []
    print(f"\n[RECENT INTERACTIONS] {len(interactions)}")
    for i in interactions[:5]:
        print(f"  - {i.get('intent','?')}: {i.get('outcome','?')}")

    # Contacts
    r3 = requests.get(f"{SUPABASE_URL}/rest/v1/contacts?select=id&limit=500", headers=headers)
    contacts = r3.json() if r3.status_code == 200 else []
    print(f"\n[CONTACTS] {len(contacts)}")

    # Memories
    r4 = requests.get(f"{SUPABASE_URL}/rest/v1/memories?select=id,memory_type&limit=500", headers=headers)
    memories = r4.json() if r4.status_code == 200 else []
    mem_types = Counter([m.get("memory_type") for m in memories])
    print(f"[MEMORIES] {len(memories)}")
    for t, c in mem_types.most_common():
        print(f"  {t}: {c}")

    # Event log
    r5 = requests.get(f"{SUPABASE_URL}/rest/v1/event_log?select=event_type,success&order=created_at.desc&limit=20", headers=headers)
    events = r5.json() if r5.status_code == 200 else []
    if events:
        successes = sum(1 for e in events if e.get("success"))
        print(f"\n[RECENT EVENTS] {len(events)} ({successes} success)")

    return {"leads": len(leads), "contacts": len(contacts), "memories": len(memories), "interactions": len(interactions)}

if __name__ == "__main__":
    monitor()
