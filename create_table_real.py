
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

CREATE_CALLS_SQL = """
CREATE TABLE IF NOT EXISTS call_transcripts (
    id SERIAL PRIMARY KEY,
    call_id TEXT UNIQUE NOT NULL,
    assistant_id TEXT,
    assistant_name TEXT,
    customer_phone TEXT,
    customer_name TEXT,
    status TEXT,
    duration_seconds NUMERIC,
    transcript TEXT,
    summary TEXT,
    analysis JSONB,
    structured_data JSONB,
    success_evaluation TEXT,
    cost NUMERIC,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    learnings_extracted BOOLEAN DEFAULT FALSE,
    sentiment TEXT
);
"""

CREATE_MEMORY_SQL = """
CREATE TABLE IF NOT EXISTS system_memory (
    id SERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    last_updated TIMESTAMPTZ DEFAULT NOW()
);
"""

def create_tables():
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Creating call_transcripts table...")
        cur.execute(CREATE_CALLS_SQL)
        
        print("Creating system_memory table...")
        cur.execute(CREATE_MEMORY_SQL)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tables created successfully.")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()
