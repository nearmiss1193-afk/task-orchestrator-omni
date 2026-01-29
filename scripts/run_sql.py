import os
import psycopg2
from dotenv import load_dotenv

def run_migration():
    load_dotenv(".env")
    db_url = os.getenv("DATABASE_URL")
    sql_path = "sql/2026_consent_defense.sql"
    
    if not db_url:
        print("❌ DATABASE_URL not found in .env")
        return

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        with open(sql_path, "r") as f:
            sql = f.read()
            
        print(f"🚀 Running migration: {sql_path}")
        cur.execute(sql)
        print("✅ SUCCESS: Consent Defense Layer Active.")
        
    except Exception as e:
        print(f"❌ MIGRATION FAILED: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()
