import psycopg2
import os

def create_social_table():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found")
        return
        
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # SQL DDL
        sql = """
        CREATE TABLE IF NOT EXISTS social_drafts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            lead_id UUID REFERENCES contacts_master(id),
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'draft',
            video_url TEXT,
            audit_url TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            scheduled_for TIMESTAMPTZ,
            metadata JSONB DEFAULT '{}'
        );
        """
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ social_drafts table created successfully.")
    except Exception as e:
        print(f"❌ Migration Error: {e}")

if __name__ == "__main__":
    create_social_table()
