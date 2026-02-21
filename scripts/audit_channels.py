import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env.local')
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor()

# Get touches in last 24h
cur.execute("SELECT channel, COUNT(*) FROM outbound_touches WHERE ts > NOW() - INTERVAL '24 hours' GROUP BY channel")
print('--- Channels (24h) ---')
for row in cur.fetchall():
    print(f'{row[0]}: {row[1]}')

# Get opens and replies in last 7 days
cur.execute("SELECT COUNT(*) FROM outbound_touches WHERE opened = true AND ts > NOW() - INTERVAL '7 days'")
print('\nOpens (7d):', cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM outbound_touches WHERE replied = true AND ts > NOW() - INTERVAL '7 days'")
print('Replies (7d):', cur.fetchone()[0])
