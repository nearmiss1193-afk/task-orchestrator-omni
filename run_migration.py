import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def run_migration(sql_file):
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in .env")
        return

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        with open(sql_file, 'r') as f:
            sql = f.read()
            
        print(f"🚀 Running migration: {sql_file}")
        cur.execute(sql)
        print("✅ Migration successful!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    sql_path = os.path.join("sql", "add_company_name.sql")
    run_migration(sql_path)
