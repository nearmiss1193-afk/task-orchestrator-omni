import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('.env.local')
conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
cur = conn.cursor(cursor_factory=RealDictCursor)

# Check recent email content
try:
    cur.execute("SELECT email_subject, email_body FROM outbound_touches WHERE channel = 'email' AND email_subject IS NOT NULL ORDER BY ts DESC LIMIT 3")
    print('--- Recent Emails Sent ---')
    for row in cur.fetchall():
        print(f'Subject: {row["email_subject"]}')
        print(f'Body Preview: {row["email_body"][:300]}...\n')
except Exception as e:
    print("Error fetching emails:", e)
    conn.rollback()

# Check events
try:
    cur.execute("SELECT event_type, COUNT(*) FROM resend_webhook_log GROUP BY event_type")
    print('--- Resend Events ---')
    for row in cur.fetchall():
        print(f'{row["event_type"]}: {row["count"]}')
except Exception as e:
    print('No resend_webhook_log table found or error:', e)
