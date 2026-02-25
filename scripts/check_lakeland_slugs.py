import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('C:/Users/nearm/.gemini/antigravity/scratch/empire-unified/.env')
db_url = os.environ.get('DATABASE_URL')

def check_slugs():
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("SELECT slug FROM seo_landing_pages WHERE slug LIKE '%lakeland%' LIMIT 20")
    rows = cur.fetchall()
    for row in rows:
        print(row[0])
    cur.close()
    conn.close()

if __name__ == '__main__':
    check_slugs()
