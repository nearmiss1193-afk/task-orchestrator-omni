import os
import psycopg2
import json
import uuid
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def insert_task():
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        print("✅ Connected to Database.")
        
        task_id = str(uuid.uuid4())
        payload = json.dumps({
            "email": "sql_test_user@example.com",
            "stripe_customer_id": "cus_sql_test",
            "plan": "sql_injection_test"
        })
        
        sql = f"""
        INSERT INTO public.tasks_queue (id, task_type, payload, status)
        VALUES ('{task_id}', 'provision_account', '{payload}', 'pending');
        """
        
        cur.execute(sql)
        print(f"✅ inserted task {task_id} via SQL.")
        
        conn.close()
    except Exception as e:
        print(f"❌ SQL Insert Failed: {e}")

if __name__ == "__main__":
    insert_task()
