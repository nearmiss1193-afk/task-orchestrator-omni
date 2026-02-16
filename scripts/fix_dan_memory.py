import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def fix_daniel_memory():
    print("=" * 60)
    print("FIXING DANIEL'S MEMORY LOOP")
    print("=" * 60)
    
    dan_id = "37610d10-7d62-436a-aa3b-eacd197b74bb"
    
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        
        # 1. Fetch current context
        cur.execute("SELECT context_summary FROM public.customer_memory WHERE customer_id = %s", (dan_id,))
        result = cur.fetchone()
        
        if result:
            ctx = result[0]
            if isinstance(ctx, str):
                ctx = json.loads(ctx)
            
            print(f"Current contact_name: {ctx.get('contact_name')}")
            
            # 2. Update to Daniel/Dan
            ctx['contact_name'] = 'Daniel'
            
            # 3. Update the record
            cur.execute(
                "UPDATE public.customer_memory SET context_summary = %s, customer_name = %s WHERE customer_id = %s",
                (json.dumps(ctx), "Daniel", dan_id)
            )
            
            # 4. Also check if there are other 'Michael' entries for the same phone
            # Dan's phone is +13529368152
            cur.execute(
                "UPDATE public.customer_memory SET customer_name = %s WHERE phone_number = %s",
                ("Daniel", "+13529368152")
            )
            
            conn.commit()
            print("✅ Memory fixed: 'Michael' replaced with 'Daniel'")
        else:
            print("❌ Record not found for Dan's ID")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    fix_daniel_memory()
