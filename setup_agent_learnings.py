import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def create_agent_learnings_table():
    """Create the agent_learnings table for post-task learning storage."""
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found.")
        return False

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_learnings (
                id SERIAL PRIMARY KEY,
                task TEXT NOT NULL,
                outcome TEXT,
                learnings TEXT,
                agent_name TEXT DEFAULT 'unknown',
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        conn.commit()
        print("✅ agent_learnings table created (or already exists).")
        
        # Verify
        cur.execute("SELECT COUNT(*) FROM agent_learnings;")
        count = cur.fetchone()[0]
        print(f"📊 Current learning records: {count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_agent_learnings_table()
