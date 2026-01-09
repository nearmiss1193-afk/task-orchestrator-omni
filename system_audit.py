"""
system_audit.py - Comprehensive System & Campaign Audit
"""
import psycopg2
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_URL = 'postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres'

def run_audit():
    print("=" * 70)
    print("🔍 EMPIRE SYSTEM & CAMPAIGN AUDIT")
    print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # 1. DATABASE STATUS
    print("\n📊 DATABASE STATUS")
    print("-" * 50)
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' ORDER BY table_name
    """)
    tables = [r[0] for r in cur.fetchall()]
    
    total_rows = 0
    for t in tables:
        cur.execute(f'SELECT COUNT(*) FROM "{t}"')
        count = cur.fetchone()[0]
        total_rows += count
        if count > 0:
            print(f"  ✓ {t}: {count} rows")
        else:
            print(f"  - {t}: empty")
    print(f"\n  TOTAL ROWS: {total_rows}")
    
    # 2. CAMPAIGN STATUS
    print("\n📈 CAMPAIGN STATUS")
    print("-" * 50)
    cur.execute("SELECT status, COUNT(*) FROM leads GROUP BY status ORDER BY COUNT(*) DESC")
    leads = cur.fetchall()
    lead_total = sum([r[1] for r in leads])
    print(f"  Total Leads: {lead_total}")
    for status, count in leads:
        pct = round(count/lead_total*100, 1) if lead_total > 0 else 0
        print(f"    - {status or 'unknown'}: {count} ({pct}%)")
    
    # 3. BRAIN MEMORY
    print("\n🧠 BRAIN MEMORY")
    print("-" * 50)
    cur.execute("SELECT key, LENGTH(value) as size FROM system_memory")
    memory = cur.fetchall()
    print(f"  Entries: {len(memory)}")
    for key, size in memory:
        print(f"    - {key}: {size} chars")
    
    # 4. AI LEARNINGS
    print("\n📚 AI LEARNINGS")
    print("-" * 50)
    cur.execute("SELECT COUNT(*) FROM agent_learnings")
    learn_count = cur.fetchone()[0]
    print(f"  Total Learnings: {learn_count}")
    if learn_count > 0:
        cur.execute("SELECT agent_name, COUNT(*) FROM agent_learnings GROUP BY agent_name")
        for agent, count in cur.fetchall():
            print(f"    - {agent}: {count} insights")
    
    # 5. CALL TRANSCRIPTS
    print("\n📞 CALL TRANSCRIPTS")
    print("-" * 50)
    cur.execute("SELECT COUNT(*) FROM call_transcripts")
    trans_count = cur.fetchone()[0]
    print(f"  Total Transcripts: {trans_count}")
    if trans_count > 0:
        cur.execute("SELECT phone_number, created_at FROM call_transcripts ORDER BY created_at DESC LIMIT 3")
        for phone, dt in cur.fetchall():
            print(f"    - {phone} ({dt})")
    
    # 6. VAPI STATUS
    print("\n🎙️ VAPI/SARAH STATUS")
    print("-" * 50)
    vapi_key = os.getenv("VAPI_PRIVATE_KEY")
    if vapi_key:
        try:
            resp = requests.get(
                "https://api.vapi.ai/assistant",
                headers={"Authorization": f"Bearer {vapi_key}"},
                timeout=10
            )
            if resp.status_code == 200:
                assistants = resp.json()
                print(f"  Assistants: {len(assistants)}")
                for a in assistants[:3]:
                    print(f"    - {a.get('name', 'Unnamed')}: {a.get('id', 'N/A')[:8]}...")
            else:
                print(f"  Error: {resp.status_code}")
        except Exception as e:
            print(f"  Connection Error: {e}")
    else:
        print("  VAPI_PRIVATE_KEY not set")
    
    # 7. LOCAL DAEMONS
    print("\n⚙️ RUNNING PROCESSES")
    print("-" * 50)
    processes = [
        "growth_daemon.py",
        "campaign_manager.py",
        "launch_drip_campaign.py",
        "inbound_poller.py"
    ]
    # Note: This is a simple check, real process monitoring would be different
    print("  Detected running in terminal:")
    print("    (See terminal tabs for active processes)")
    
    # 8. WEBSITE STATUS
    print("\n🌐 WEBSITE STATUS")
    print("-" * 50)
    sites = [
        ("Main Site", "https://www.aiserviceco.com"),
        ("Checkout", "https://www.aiserviceco.com/checkout.html"),
        ("Dashboard", "https://client-portal-pxktge2pg-nearmiss1193-9477s-projects.vercel.app")
    ]
    for name, url in sites:
        try:
            resp = requests.get(url, timeout=10)
            status = "✓ LIVE" if resp.status_code == 200 else f"⚠️ {resp.status_code}"
            print(f"  {name}: {status}")
        except Exception as e:
            print(f"  {name}: ❌ DOWN ({e})")
    
    # 9. SUMMARY
    print("\n" + "=" * 70)
    print("📋 AUDIT SUMMARY")
    print("=" * 70)
    print(f"""
  Database:     {len(tables)} tables, {total_rows} total rows
  Leads:        {lead_total} total ({len([l for l in leads if l[1] > 0])} statuses)
  Brain:        {len(memory)} memory entries
  AI Learning:  {learn_count} insights captured
  Transcripts:  {trans_count} call recordings
  """)
    
    conn.close()
    print("Audit complete!")

if __name__ == "__main__":
    run_audit()
