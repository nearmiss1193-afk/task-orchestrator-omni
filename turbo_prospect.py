"""TURBO PROSPECTOR - Get HVAC leads with phones NOW"""
import requests
import psycopg2
import time

APOLLO_KEY = "15jm0KLL6TrYE1OFq73CwA"

def main():
    print("=== TURBO PROSPECTOR ===")
    
    conn = psycopg2.connect(
        host="db.rzcpfwkygdvoshtwxncs.supabase.co",
        port=5432, database="postgres", user="postgres", password="Inez11752990@"
    )
    cur = conn.cursor()
    
    regions = ["Florida", "Texas", "California", "Georgia", "North Carolina"]
    added = 0
    
    for region in regions:
        print(f"\n Searching {region}...")
        try:
            resp = requests.post(
                "https://api.apollo.io/v1/mixed_companies/search",
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": APOLLO_KEY,
                    "q_keywords": "HVAC contractor",
                    "organization_locations": [f"{region}, United States"],
                    "per_page": 25,
                    "organization_num_employees_ranges": ["1,10", "11,50"]
                },
                timeout=30
            )
            if resp.status_code == 200:
                orgs = resp.json().get("organizations", [])
                for org in orgs:
                    name = org.get("name", "")
                    phone = org.get("phone")
                    if not name or not phone:
                        continue
                    
                    # Check if valid US phone
                    if not phone.startswith("+1") and not phone.startswith("1"):
                        continue
                    
                    # Check duplicate
                    cur.execute("SELECT id FROM leads WHERE company_name = %s", (name,))
                    if cur.fetchone():
                        continue
                    
                    # Insert
                    cur.execute("""
                        INSERT INTO leads (company_name, phone, website_url, city, state, industry, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (name, phone, org.get("website_url"), org.get("city"), region, "HVAC", "new"))
                    conn.commit()
                    print(f"   ✅ {name}: {phone}")
                    added += 1
            elif resp.status_code == 422:
                print(f"   ⚠️ Rate limited")
                time.sleep(10)
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n=== ADDED {added} NEW HVAC LEADS ===")
    
    # Show ready leads
    cur.execute("SELECT COUNT(*) FROM leads WHERE status = 'new' AND phone IS NOT NULL")
    print(f"Total NEW leads with phone: {cur.fetchone()[0]}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
