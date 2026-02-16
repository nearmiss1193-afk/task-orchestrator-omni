from modules.database.supabase_client import get_supabase
import os

def check_constraints():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
        
    import psycopg2
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    print("--- CHECK CONSTRAINTS: system_state ---")
    query = """
    SELECT conname, pg_get_constraintdef(c.oid)
    FROM pg_constraint c
    JOIN pg_class t ON t.oid = c.conrelid
    WHERE t.relname = 'system_state';
    """
    cur.execute(query)
    for row in cur.fetchall():
        print(f"Name: {row[0]}")
        print(f"Def:  {row[1]}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_constraints()
