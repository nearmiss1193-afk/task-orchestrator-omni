"""Check valid leads with phones for contactor"""
import psycopg2
import re

conn = psycopg2.connect(
    host="db.rzcpfwkygdvoshtwxncs.supabase.co",
    port=5432, database="postgres", user="postgres", password="Inez11752990@"
)
cur = conn.cursor()

# Get leads with phones that aren't fake
cur.execute("""
    SELECT company_name, phone FROM leads 
    WHERE status = 'new' AND phone IS NOT NULL 
    AND phone NOT LIKE '%9999%' 
    AND phone NOT LIKE '%0000%'
    AND phone NOT LIKE '%555%'
""")
rows = cur.fetchall()

print(f"Valid NEW leads ready for contact: {len(rows)}")
for company, phone in rows[:15]:
    print(f"  {company}: {phone}")

cur.close()
conn.close()
