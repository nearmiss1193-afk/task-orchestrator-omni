import psycopg2

DB_URL = 'postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres'

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

print("=" * 50)
print("CAMPAIGN STATUS")
print("=" * 50)

# Leads
print("\n📊 LEADS:")
cur.execute("SELECT status, COUNT(*) FROM leads GROUP BY status ORDER BY COUNT(*) DESC")
for r in cur.fetchall():
    print(f"  {r[0] or 'null'}: {r[1]}")

# Outbound
print("\n📤 OUTBOUND EVENTS:")
cur.execute("SELECT event_type, COUNT(*) FROM outbound_events GROUP BY event_type")
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f"  {r[0]}: {r[1]}")
else:
    print("  No outbound events recorded yet")

# Brain memory
print("\n🧠 BRAIN MEMORY:")
cur.execute("SELECT key FROM system_memory")
for r in cur.fetchall():
    print(f"  - {r[0]}")

conn.close()
print("\n" + "=" * 50)
