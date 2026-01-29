import os
import psycopg2
import json
from dotenv import load_dotenv

load_dotenv(".env")
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT metadata FROM contacts_master WHERE metadata IS NOT NULL LIMIT 5")
    rows = cur.fetchall()
    for i, row in enumerate(rows):
        metadata = row[0]
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except:
                pass
        print(f"--- Lead {i+1} Metadata ---")
        print(json.dumps(metadata, indent=2) if isinstance(metadata, dict) else metadata)
        if isinstance(metadata, dict) and "locationId" in metadata:
            print(f"📍 Found LocationId: {metadata['locationId']}")
            
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
