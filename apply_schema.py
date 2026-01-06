import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL missing in .env")
    exit(1)

sql_file = "c:\\Users\\nearm\\.gemini\\antigravity\\scratch\\empire-unified\\schema_assets.sql"

try:
    print(f"🔗 Connecting to Supabase Postgres...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    with open(sql_file, 'r') as f:
        sql = f.read()
        print(f"📜 Applying Schema...")
        cur.execute(sql)
        conn.commit()
    
    print("✅ Schema applied successfully. Table 'asset_inbox' should now exist.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Failed to apply schema: {e}")
