import psycopg2

db_url = 'postgresql://postgres:Inez11752990%40@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres'

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print('=' * 50)
    print('DATABASE SCHEMA CHECK')
    print('=' * 50)
    
    # List all tables
    print('\n1. TABLES:')
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = [r[0] for r in cur.fetchall()]
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        print(f'   {t}: {count} rows')
    
    # Check system_memory schema
    print('\n2. SYSTEM_MEMORY COLUMNS:')
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'system_memory'
    """)
    for r in cur.fetchall():
        print(f'   {r[0]}: {r[1]}')
    
    # Check leads status
    print('\n3. LEADS BY STATUS:')
    cur.execute("SELECT status, COUNT(*) FROM leads GROUP BY status ORDER BY COUNT(*) DESC")
    for r in cur.fetchall():
        print(f'   {r[0] or "null"}: {r[1]}')
        
    conn.close()
    print('\n' + '=' * 50)
except Exception as e:
    print(f'Error: {e}')
