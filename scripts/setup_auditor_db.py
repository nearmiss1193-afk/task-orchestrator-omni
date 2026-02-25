import os
from dotenv import load_dotenv
import psycopg2

load_dotenv('C:/Users/nearm/.gemini/antigravity/scratch/empire-unified/.env')
db_url = os.environ.get('DATABASE_URL')

def setup_telemetry():
    print("🚀 Connecting to Supabase to build Auditor telemetry table...")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS page_health_logs (
            url_slug TEXT PRIMARY KEY,
            status_code INTEGER,
            schema_present BOOLEAN,
            ai_content_verified BOOLEAN,
            fcp_ms INTEGER,
            last_checked TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ `page_health_logs` table created successfully in Supabase.")

if __name__ == '__main__':
    setup_telemetry()
