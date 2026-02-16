import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def list_schema():
    print("=" * 60)
    print("DATABASE SCHEMA INSPECTION")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        tables = ['outbound_touches', 'contacts_master', 'vapi_debug_logs', 'system_health_log', 'system_state']
        
        for table in tables:
            print(f"\n[TABLE: {table}]")
            cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position")
            cols = cur.fetchall()
            for col, dtype in cols:
                print(f"  - {col:30} {dtype}")
                
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

if __name__ == "__main__":
    list_schema()
