import os
import sys
import requests

# Set env vars BEFORE importing memory
# Test with ANON KEY (Simulate old Railway Env)
os.environ["NEXT_PUBLIC_SUPABASE_URL"] = "https://rzcpfwkygdvoshtwxncs.supabase.co"
# ANON KEY from temp_env.txt
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1OTA0MjQsImV4cCI6MjA4MjE2NjQyNH0.hX9Jc_3F5qg7aI5y2-d2j81b2t_2_7f1y5w6g4s0a8"
os.environ["SUPABASE_URL"] = "https://rzcpfwkygdvoshtwxncs.supabase.co"
os.environ["SUPABASE_KEY"] = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

# Import memory module (make sure it's in path)
sys.path.append(os.getcwd())
try:
    from memory import resolve_or_create_contact
except ImportError:
    print("[DEBUG] Import failed. Ensure memory.py is in current dir.")
    sys.exit(1)

def test_logic():
    print("[DEBUG] Testing individual operations...")
    
    # 1. Test INSERT - Minimal (Phone Only)
    print("\n[TEST 1A] Testing INSERT (Phone Only)...")
    try:
        new_row = {"phone": "+18888888888"}
        res = requests.post(
            f"{os.environ['SUPABASE_URL']}/rest/v1/contact_profiles",
            headers={
                "apikey": os.environ['SUPABASE_KEY'],
                "Authorization": f"Bearer {os.environ['SUPABASE_KEY']}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=new_row
        )
        print(f"INSERT Phone Status: {res.status_code}")
        if not res.ok:
            print(f"INSERT Phone Error: {res.text}")
        else:
            print(f"INSERT Phone Success: {res.json()}")
    except Exception as e:
        print(f"INSERT Phone Exception: {e}")

    # 1B. Test INSERT - Phone + GHL ID
    print("\n[TEST 1B] Testing INSERT (Phone + GHL ID)...")
    try:
        new_row = {"phone": "+17777777777", "ghl_contact_id": "debug_col_test_1"}
        res = requests.post(
            f"{os.environ['SUPABASE_URL']}/rest/v1/contact_profiles",
            headers={
                "apikey": os.environ['SUPABASE_KEY'],
                "Authorization": f"Bearer {os.environ['SUPABASE_KEY']}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=new_row
        )
        print(f"INSERT GHL Status: {res.status_code}")
        if not res.ok:
            print(f"INSERT GHL Error: {res.text}")
        else:
            print(f"INSERT GHL Success: {res.json()}")
    except Exception as e:
        print(f"INSERT GHL Exception: {e}")

    # 1C. Test INSERT - Phone + Company
    print("\n[TEST 1C] Testing INSERT (Phone + Company)...")
    try:
        new_row = {"phone": "+16666666666", "company_name": "Debug Inc"}
        res = requests.post(
            f"{os.environ['SUPABASE_URL']}/rest/v1/contact_profiles",
            headers={
                "apikey": os.environ['SUPABASE_KEY'],
                "Authorization": f"Bearer {os.environ['SUPABASE_KEY']}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=new_row
        )
        print(f"INSERT Company Status: {res.status_code}")
        if not res.ok:
            print(f"INSERT Company Error: {res.text}")
        else:
            print(f"INSERT Company Success: {res.json()}")
    except Exception as e:
        print(f"INSERT Company Exception: {e}")

    # 1D. Test INSERT - Empty Object
    print("\n[TEST 1D] Testing INSERT (Empty Object)...")
    try:
        new_row = {}
        res = requests.post(
            f"{os.environ['SUPABASE_URL']}/rest/v1/contact_profiles",
            headers={
                "apikey": os.environ['SUPABASE_KEY'],
                "Authorization": f"Bearer {os.environ['SUPABASE_KEY']}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=new_row
        )
        print(f"INSERT Empty Status: {res.status_code}")
        if not res.ok:
            print(f"INSERT Empty Error: {res.text}")
        else:
            print(f"INSERT Empty Success: {res.json()}")
    except Exception as e:
        print(f"INSERT Empty Exception: {e}")



    # 2. Test GET by GHL_ID
    print("\n[TEST 2] Testing GET by ghl_contact_id...")
    try:
        res = requests.get(
            f"{os.environ['SUPABASE_URL']}/rest/v1/contact_profiles?ghl_contact_id=eq.debug_test_123&limit=1",
            headers={
                "apikey": os.environ['SUPABASE_KEY'],
                "Authorization": f"Bearer {os.environ['SUPABASE_KEY']}"
            }
        )
        print(f"GET Status: {res.status_code}")
        if not res.ok:
            print(f"GET Error: {res.text}")
        else:
            print(f"GET Success: {res.json()}")
    except Exception as e:
        print(f"GET Exception: {e}")



if __name__ == "__main__":
    test_logic()
