import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env")
db_url = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    # Check for the latest SMS touch for the commander's phone
    phone = "+13529368152"
    cur.execute("SELECT channel, status, ts FROM outbound_touches WHERE phone = %s ORDER BY ts DESC LIMIT 1", (phone,))
    row = cur.fetchone()
    if row:
        print(f"✅ STRIKE VERIFIED: Channel: {row[0]} | Status: {row[1]} | Timestamp: {row[2]}")
    else:
        print(f"⚠️ NO STRIKE RECORD FOUND for {phone}")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
