"""
check_brain_status.py - Check if brain is collecting info
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("ERROR: DATABASE_URL not found in .env")
    exit(1)

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("=" * 60)
    print("BRAIN STATUS CHECK")
    print("=" * 60)
    
    # Check system_memory table
    print("\n1. SYSTEM MEMORY TABLE:")
    cur.execute("SELECT key, value, updated_at FROM system_memory ORDER BY updated_at DESC LIMIT 5")
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(f"   {row[0]}: {str(row[1])[:50]}... ({row[2]})")
    else:
        print("   No entries found")
    
    # Check agent_learnings table
    print("\n2. AGENT LEARNINGS TABLE:")
    cur.execute("""
        SELECT agent_name, topic, insight, created_at 
        FROM agent_learnings 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(f"   [{row[0]}] {row[1]}: {str(row[2])[:40]}... ({row[3]})")
    else:
        print("   No learnings recorded yet")
    
    # Check leads
    print("\n3. LEAD PIPELINE:")
    cur.execute("SELECT status, COUNT(*) FROM leads GROUP BY status ORDER BY COUNT(*) DESC")
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(f"   {row[0] or 'unknown'}: {row[1]}")
    else:
        print("   No leads found")
    
    # Check outbound events
    print("\n4. OUTBOUND EVENTS:")
    cur.execute("SELECT event_type, COUNT(*) FROM outbound_events GROUP BY event_type")
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(f"   {row[0]}: {row[1]}")
    else:
        print("   No outbound events")
    
    # Check transcripts
    print("\n5. CALL TRANSCRIPTS:")
    cur.execute("SELECT COUNT(*) FROM transcripts")
    count = cur.fetchone()[0]
    print(f"   Total: {count}")
    
    conn.close()
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"Database Error: {e}")
