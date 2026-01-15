"""Direct DB enrichment - bypass Supabase client issues"""
import psycopg2
import requests

# Direct connection via transaction pooler
APOLLO_KEY = "15jm0KLL6TrYE1OFq73CwA"

def enrich_lead(email):
    """Get phone from Apollo"""
    try:
        resp = requests.post(
            "https://api.apollo.io/v1/people/match",
            headers={"Content-Type": "application/json"},
            json={"api_key": APOLLO_KEY, "email": email, "reveal_phone_number": True},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json().get("person", {})
            phones = data.get("phone_numbers", [])
            if phones:
                return phones[0].get("sanitized_number")
        elif resp.status_code == 429:
            print("   Apollo rate limited")
            return "RATE_LIMIT"
    except Exception as e:
        print(f"   Error: {e}")
    return None

def main():
    conn = psycopg2.connect(
        host="db.rzcpfwkygdvoshtwxncs.supabase.co",
        port=5432,
        database="postgres",
        user="postgres",
        password="Inez11752990@"
    )
    cur = conn.cursor()
    
    # Get leads without phones
    cur.execute("SELECT id, company_name, email FROM leads WHERE phone IS NULL AND email IS NOT NULL LIMIT 25")
    leads = cur.fetchall()
    print(f"Found {len(leads)} leads to enrich")
    
    enriched = 0
    for lead_id, name, email in leads:
        print(f"Enriching {name} ({email})...")
        phone = enrich_lead(email)
        if phone == "RATE_LIMIT":
            print("   Stopping due to rate limit")
            break
        if phone:
            cur.execute("UPDATE leads SET phone = %s WHERE id = %s", (phone, lead_id))
            conn.commit()
            print(f"   ✓ Phone: {phone}")
            enriched += 1
        else:
            print("   ✗ No phone")
    
    # Check results
    cur.execute("SELECT COUNT(*) FROM leads WHERE phone IS NOT NULL")
    total_with_phone = cur.fetchone()[0]
    print(f"\n=== ENRICHED {enriched} LEADS ===")
    print(f"=== TOTAL LEADS WITH PHONE: {total_with_phone} ===")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
