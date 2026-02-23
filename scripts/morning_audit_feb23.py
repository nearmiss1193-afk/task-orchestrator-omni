import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ.get('NEON_DATABASE_URL') or os.environ.get('DATABASE_URL')

def run_audit():
    print("========================================")
    print("  INCOME PIPELINE CONFIRMATION REPORT   ")
    print(f"  DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ")
    print("========================================")

    if not DATABASE_URL:
        print("❌ Missing DATABASE_URL")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Step 1: SENDING? -> outbound_touches last 24h
        cur.execute("SELECT COUNT(*) FROM outbound_touches WHERE ts > NOW() - INTERVAL '24 hours'")
        sending_24h = cur.fetchone()[0]
        
        # Step 2: OPENING? -> opened = true last 7d
        # We might not have 'opened' column. Let's try, catch if missing.
        try:
            cur.execute("SELECT COUNT(*) FROM outbound_touches WHERE opened = true AND ts > NOW() - INTERVAL '7 days'")
            opening_7d = cur.fetchone()[0]
        except psycopg2.errors.UndefinedColumn:
            conn.rollback() # reset transaction
            cur.execute("SELECT count(*) FROM outbound_touches WHERE status = 'opened' AND ts > NOW() - INTERVAL '7 days'")
            opening_7d = cur.fetchone()[0]

        # Step 3: REPLYING? -> replied = true last 7d
        try:
            cur.execute("SELECT COUNT(*) FROM outbound_touches WHERE replied = true AND ts > NOW() - INTERVAL '7 days'")
            replying_7d = cur.fetchone()[0]
        except psycopg2.errors.UndefinedColumn:
            conn.rollback()
            cur.execute("SELECT count(*) FROM outbound_touches WHERE status = 'replied' AND ts > NOW() - INTERVAL '7 days'")
            replying_7d = cur.fetchone()[0]

        # Step 6: PIPELINE? -> contacts_master
        cur.execute("SELECT COUNT(*) FROM contacts_master WHERE status IN ('new', 'research_done')")
        pipeline_count = cur.fetchone()[0]
        
        # Phase 14 (Bid-Bot)
        cur.execute("SELECT COUNT(*) FROM bids")
        bids_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM bids WHERE created_at > NOW() - INTERVAL '12 hours'")
        bids_new = cur.fetchone()[0]

        # Phase 15 (Intent Engine)
        cur.execute("SELECT COUNT(*) FROM estate_sales")
        estate_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM estate_sales WHERE created_at > NOW() - INTERVAL '12 hours'")
        estate_new = cur.fetchone()[0]

        print(f"Step 1: SENDING?    -> {sending_24h} emails in last 24h")
        print(f"Step 2: OPENING?    -> {opening_7d} opens in last 7d")
        print(f"Step 3: REPLYING?   -> {replying_7d} replies in last 7d")
        print(f"Step 4: BOOKING?    -> [Check GHL manually for appointments]")
        print(f"Step 5: PAYING?     -> [Check Stripe manually for payments]")
        print(f"Step 6: PIPELINE?   -> {pipeline_count} contactable leads remain")
        print("-" * 40)
        print("🧠 ABACUS.AI SCRAPER TELEMETRY (PHASE 14 & 15)")
        print(f"🏢 B2G Bids Total: {bids_count} | Captured today: {bids_new}")
        print(f"🏡 B2C Estates Total: {estate_count} | Captured today: {estate_new}")
        print("========================================")

    except Exception as e:
        print(f"❌ DB Error: {e}")

if __name__ == "__main__":
    run_audit()
