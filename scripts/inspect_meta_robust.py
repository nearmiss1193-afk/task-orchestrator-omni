import os
import psycopg2
import json
from dotenv import load_dotenv

load_dotenv(".env")
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    # Get one row and its columns
    cur.execute("SELECT * FROM contacts_master LIMIT 1")
    row = cur.fetchone()
    if row:
        colnames = [desc[0] for desc in cur.description]
        data = dict(zip(colnames, row))
        print("--- Lead Data (Dict) ---")
        print(json.dumps(data, indent=2, default=str))
        
        # Check for LocationID in 'meta'
        meta = data.get("meta")
        if meta:
            if isinstance(meta, str):
                try: meta = json.loads(meta)
                except: pass
            if isinstance(meta, dict) and "locationId" in meta:
                print(f"📍 Found LocationId: {meta['locationId']}")
            elif isinstance(meta, dict):
                print(f"📋 Meta keys: {list(meta.keys())}")
    else:
        print("⚠️ No leads found.")
            
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
