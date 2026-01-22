from supabase import create_client
import os

SUB_URL = 'https://rzcpfwkygdvoshtwxncs.supabase.co'
SUB_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo'

def check_amos():
    supabase = create_client(SUB_URL, SUB_KEY)
    tables = ["system_state", "system_health", "lessons_learned", "buildable_components"]
    results = {}
    
    for t in tables:
        try:
            # Check if table exists by doing a minimal select
            res = supabase.table(t).select("count", count="exact").limit(1).execute()
            results[t] = "EXISTS"
        except Exception as e:
            results[t] = "MISSING"
            
    return results

if __name__ == "__main__":
    print("--- AMOS DIAGNOSTIC ---")
    status = check_amos()
    for t, s in status.items():
        print(f"{t}: {s}")
