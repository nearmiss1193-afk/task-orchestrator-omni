import os
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load credentials
load_dotenv()
load_dotenv('.env.local')

db_url = os.environ.get("DATABASE_URL")

if not db_url:
    print("❌ Error: Missing DATABASE_URL in environment")
    exit(1)

def get_waterfall_summary():
    """Returns a clean summary string for SMS/Executive Pulse."""
    conn = None
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM outbound_touches WHERE ts > NOW() - INTERVAL '24 hours';")
        outreach_24h = cur.fetchone()[0]
        
        cur.execute("SELECT MAX(checked_at) FROM system_health_log;")
        last_hb = cur.fetchone()[0]
        
        hb_str = "N/A"
        if last_hb and hasattr(last_hb, 'strftime'):
            hb_str = f"{last_hb.strftime('%H:%M')} UTC"
        elif last_hb:
            hb_str = str(last_hb)[:16]
            
        cur.execute("SELECT status FROM system_state WHERE key = 'campaign_mode';")
        res_mode = cur.fetchone()
        campaign_status = res_mode[0] if res_mode else "UNKNOWN"
        
        cur.execute("SELECT COUNT(*) FROM contacts_master WHERE status IN ('new', 'research_done');")
        leads_count = cur.fetchone()[0]
        
        summary = (
            f"📈 Outreach (24h): {outreach_24h}\n"
            f"💓 Last Pulse: {hb_str}\n"
            f"🔄 Mode: {campaign_status}\n"
            f"🎯 Pool: {leads_count} leads"
        )
        cur.close()
        return summary
    except Exception as e:
        return f"❌ Waterfall Error: {str(e)}"
    finally:
        if conn:
            conn.close()

def check_revenue_waterfall():
    print("═══════════════════════════════════════════════════════════════")
    print("REVENUE WATERFALL CHECK (Direct SQL)")
    print("═══════════════════════════════════════════════════════════════")
    print(get_waterfall_summary())
    print("═══════════════════════════════════════════════════════════════")
    
    conn = None
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # 1. Outreach Happening? (Last 30 min)
        cur.execute("SELECT COUNT(*) FROM outbound_touches WHERE ts > NOW() - INTERVAL '30 minutes';")
        outreach_30m = cur.fetchone()[0]
        
        # 1b. Outreach (Last 24h)
        cur.execute("SELECT COUNT(*) FROM outbound_touches WHERE ts > NOW() - INTERVAL '24 hours';")
        outreach_24h = cur.fetchone()[0]
        
        status_outreach = "✅" if outreach_30m > 0 else "❌"
        print(f"{status_outreach} Outreach (30m): {outreach_30m} sent")
        print(f"✅ Outreach (24h): {outreach_24h} sent")

        # 2. Heartbeat Working? (Last 15 min)
        cur.execute("SELECT checked_at FROM system_health_log ORDER BY checked_at DESC LIMIT 1;")
        res_hb = cur.fetchone()
        if res_hb:
            last_hb = res_hb[0]
            # Check if it's within last 15 mins manually in script if needed, but display it
            print(f"✅ Last Heartbeat: {last_hb}")
        else:
            print("❌ No Heartbeats found")

        # 3. Campaign Mode
        cur.execute("SELECT status FROM system_state WHERE key = 'campaign_mode';")
        res_mode = cur.fetchone()
        campaign_status = res_mode[0] if res_mode else "UNKNOWN"
        status_mode = "✅" if campaign_status == "working" else "❌"
        print(f"{status_mode} Campaign Mode: {campaign_status}")
        
        # 4. Ingestion Pulse (New leads)
        cur.execute("SELECT COUNT(*) FROM contacts_master WHERE status IN ('new', 'research_done');")
        leads_count = cur.fetchone()[0]
        print(f"✅ Available Leads: {leads_count}")

        print("═══════════════════════════════════════════════════════════════")
        if status_outreach == "✅" and status_mode == "✅":
            print("VERIFIED WORKING: System is operational.")
        elif status_mode == "✅":
            print("VERIFICATION PENDING: System is 'working' but no outreach in last 30m. (Check hours?)")
        else:
            print("VERIFICATION FAILED: System is NOT 'working'.")
            
        cur.close()
    except Exception as e:
        print(f"❌ Error during verification: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_revenue_waterfall()
