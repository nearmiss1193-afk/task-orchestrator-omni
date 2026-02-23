import psycopg2

DATABASE_URL = "postgresql://postgres:Inez11752990@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres"

def add_body_column():
    print("🐘 DATABASE: Adding `body` column to outbound_touches...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("""
            ALTER TABLE outbound_touches 
            ADD COLUMN IF NOT EXISTS body TEXT;
        """)
        
        conn.commit()
        print("✅ Column `body` added to outbound_touches successfully.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    add_body_column()
