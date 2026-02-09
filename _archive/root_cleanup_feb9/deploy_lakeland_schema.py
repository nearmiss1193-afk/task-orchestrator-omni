
import os
import psycopg2
from urllib.parse import urlparse

def deploy_schema():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL missing")
        return

    schema_path = "sql/lakeland_os_schema.sql"
    if not os.path.exists(schema_path):
        print(f"❌ Error: {schema_path} not found")
        return

    print(f"🚀 SCHEMA DEP: Deploying {schema_path} to Supabase...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        with open(schema_path, 'r') as f:
            sql = f.read()
            
        cur.execute(sql)
        print("✅ Lakeland Local OS Schema Deployed.")
        conn.close()
    except Exception as e:
        print(f"❌ Schema Deployment Failed: {e}")

if __name__ == "__main__":
    deploy_schema()
