import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def deep_scan():
    print("=" * 60)
    print("DEEP STORAGE SCAN")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # 1. Check current database and user
        cur.execute("SELECT current_database(), current_user")
        db, user = cur.fetchone()
        print(f"DATABASE: {db} | USER: {user}")
        
        # 2. List all tables across all schemas (excluding system schemas)
        print("\n[NON-SYSTEM TABLES FOUND]")
        cur.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name
        """)
        tables = cur.fetchall()
        for schema, name in tables:
            print(f"  {schema:15} | {name}")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

if __name__ == "__main__":
    deep_scan()
