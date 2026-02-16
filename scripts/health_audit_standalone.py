import modal

app = modal.App("standalone-health-audit")

# Simple base image for diagnostics
image = modal.Image.debian_slim().pip_install("supabase")
VAULT = modal.Secret.from_name("sovereign-vault")

@app.function(image=image, secrets=[VAULT])
def check_health():
    import os
    from supabase import create_client
    from datetime import datetime, timedelta
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Credentials missing")
        return
        
    sb = create_client(url, key)
    
    print(f"\n{'='*40}")
    print(f"📊 LIVE AUDIT: {datetime.utcnow().isoformat()}")
    print(f"{'='*40}")
    
    # 1. Outreach Truth
    print("\n📢 OUTREACH (outbound_touches):")
    touches = sb.table("outbound_touches").select("ts").order("ts", desc=True).limit(5).execute()
    total_24h = sb.table("outbound_touches").select("id", count="exact").filter("ts", "gt", (datetime.utcnow() - timedelta(days=1)).isoformat()).execute().count
    
    print(f" - Last 24h Total: {total_24h}")
    if touches.data:
        for t in touches.data:
            print(f"   • {t['ts']}")
    else:
        print("   • NO DATA FOUND")

    # 2. Heartbeat check
    print("\n❤️ HEARTBEATS (system_health_log):")
    heartbeats = sb.table("system_health_log").select("checked_at, status").order("checked_at", desc=True).limit(3).execute()
    if heartbeats.data:
        for hb in heartbeats.data:
            print(f"   • {hb['checked_at']} | {hb['status']}")
    else:
        print("   • NO DATA FOUND")

    # 3. Campaign Status
    print("\n⚙️ SYSTEM STATE:")
    mode = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
    status = mode.data[0].get("status") if mode.data else "UNKNOWN"
    print(f" - campaign_mode: {status}")

    # 4. Lead Pulse
    print("\n👥 LEAD STATUS (contacts_master):")
    leads = sb.table("contacts_master").select("status").execute()
    summary = {}
    for l in leads.data:
        summary[l['status']] = summary.get(l['status'], 0) + 1
    
    for s, count in summary.items():
        print(f" - {s}: {count}")

if __name__ == "__main__":
    with app.run():
        check_health.remote()
