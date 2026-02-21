import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env.local')
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()

try:
    cur.execute("UPDATE system_state SET status = 'working' WHERE key = 'campaign_mode'")
    conn.commit()
    print("✅ Campaign mode flipped to: working")
except Exception as e:
    print("❌ Error:", e)
    conn.rollback()
finally:
    conn.close()
