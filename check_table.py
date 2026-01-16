import psycopg2

DB_URL = "postgresql://postgres:Inez11752990@db.rzcpfwkygdvoshtwxncs.supabase.co:5432/postgres"

def check():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    # Get all indices and constraints for 'leads'
    cur.execute("""
        SELECT
            ix.relname as index_name,
            a.attname as column_name,
            indisunique as is_unique
        FROM
            pg_class t,
            pg_class ix,
            pg_index i,
            pg_attribute a
        WHERE
            t.oid = i.indrelid
            AND ix.oid = i.indexrelid
            AND a.attrelid = t.oid
            AND a.attnum = ANY(i.indkey)
            AND t.relkind = 'r'
            AND t.relname = 'leads'
    """)
    print("Indices on 'leads' table:")
    for row in cur.fetchall():
        print(row)
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    check()
