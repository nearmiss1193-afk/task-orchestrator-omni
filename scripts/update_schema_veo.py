import os
import psycopg2
from dotenv import load_dotenv

def migrate():
    load_dotenv()
    db_url = os.environ.get("NEON_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        print("Missing DATABASE_URL")
        return
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Adding veo_status column...")
        cur.execute("ALTER TABLE contacts_master ADD COLUMN IF NOT EXISTS veo_status VARCHAR DEFAULT 'none';")
        
        print("Adding veo_video_url column...")
        cur.execute("ALTER TABLE contacts_master ADD COLUMN IF NOT EXISTS veo_video_url VARCHAR;")
        
        print("Migration complete.")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Migration Failed: {e}")

if __name__ == "__main__":
    migrate()
