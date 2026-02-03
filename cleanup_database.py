import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

def cleanup_duplicates():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in .env")
        return

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        print("🧼 Cleaning up duplicate emails in contacts_master...")
        
        # SQL to delete duplicates keeping the latest one
        cleanup_sql = """
        DELETE FROM contacts_master a
        USING contacts_master b
        WHERE a.id < b.id
        AND a.email = b.email;
        """
        
        cur.execute(cleanup_sql)
        print(f"✅ Deleted {cur.rowcount} duplicate rows.")
        
        # Now try to add the constraint again
        print("🛡️ Adding UNIQUE constraint to email...")
        constraint_sql = "ALTER TABLE contacts_master ADD CONSTRAINT unique_email UNIQUE (email);"
        cur.execute(constraint_sql)
        print("✅ UNIQUE constraint added successfully!")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

if __name__ == "__main__":
    cleanup_duplicates()
