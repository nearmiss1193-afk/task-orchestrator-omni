import modal
from deploy import image, VAULT

app = modal.App("outreach-audit")

@app.function(image=image, secrets=[VAULT])
def run_health_check():
    from modules.database.supabase_client import get_supabase
    import json
    from datetime import datetime, timedelta
    
    sb = get_supabase()
    if not sb:
        print("❌ Supabase client failed")
        return
        
    print(f"📊 SYSTEM AUDIT: {datetime.utcnow().isoformat()}")
    
    # 1. Outreach Count (Truth Test)
    touches = sb.table("outbound_touches").select("ts").order("ts", desc=True).limit(50).execute()
    total_24h = sb.table("outbound_touches").select("id", count="exact").filter("ts", "gt", (datetime.utcnow() - timedelta(days=1)).isoformat()).execute().count
    total_1h = sb.table("outbound_touches").select("id", count="exact").filter("ts", "gt", (datetime.utcnow() - timedelta(hours=1)).isoformat()).execute().count
    
    print(f"\n📢 OUTREACH METRICS:")
    print(f" - Last 24 hours: {total_24h} touches")
    print(f" - Last 60 minutes: {total_1h} touches")
    if touches.data:
        print(f" - Most recent touch: {touches.data[0]['ts']}")
    else:
        print(" - Most recent touch: NEVER")

    # 2. Heartbeat (Service Pulse)
    heartbeats = sb.table("system_health_log").select("checked_at, status").order("checked_at", desc=True).limit(5).execute()
    print(f"\n❤️ HEARTBEAT LOGS:")
    if heartbeats.data:
        for hb in heartbeats.data:
            print(f" - {hb['checked_at']} | {hb['status']}")
    else:
        print(" - NO HEARTBEATS FOUND")

    # 3. Campaign & Leads (Potential)
    mode = sb.table("system_state").select("status").eq("key", "campaign_mode").execute()
    campaign_status = mode.data[0].get("status") if mode.data else "MISSING"
    
    leads = sb.table("contacts_master").select("status", count="exact").execute()
    lead_summary = {}
    if leads.data:
        # Aggregating manually if needed, but the select with count might return filtered
        # Let's get a group by count
        r = sb.table("contacts_master").select("status").execute()
        for l in r.data:
            s = l['status']
            lead_summary[s] = lead_summary.get(s, 0) + 1

    print(f"\n⚙️ SYSTEM STATE:")
    print(f" - Campaign Mode: {campaign_status}")
    print(f" - Lead Pipeline: {lead_summary}")

if __name__ == "__main__":
    with app.run():
        run_health_check.remote()
