import os
import psycopg2
from dotenv import load_dotenv

# Load env from root
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def apply_indexes():
    if not DB_URL:
        print("❌ DATABASE_URL not found in environment.")
        return

    print(f"🔌 Connecting to Supabase...")
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        print("⚡ Creating optimization indexes...")
        
        # 1. Status + Created At (Speed up "Find New Leads" loop)
        # Used by: lead_research_loop
        print("   -> Index: idx_contacts_status_created...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_contacts_status_created ON contacts_master(status, created_at DESC);")
        
        # 2. GHL Contract ID (Speed up "Get Contact by ID")
        # Used by: dispatch_email_logic, spartan_responder
        print("   -> Index: idx_contacts_ghl_id...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_contacts_ghl_id ON contacts_master(ghl_contact_id);")

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database optimization complete.")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    apply_indexes()
