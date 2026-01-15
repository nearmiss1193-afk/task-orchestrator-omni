"""Enrich leads with Lusha API - works better for company data"""
import psycopg2
import requests
import time

# Credentials
LUSHA_API_KEY = "5ad17deb-fe1d-4239-9fb6-eb680340b810"

def enrich_with_lusha(company_name, website=None):
    """Get phone from Lusha company API"""
    try:
        headers = {"api_key": LUSHA_API_KEY, "Content-Type": "application/json"}
        
        # Try company enrich endpoint
        url = f"https://api.lusha.com/company"
        params = {"company": company_name}
        if website:
            domain = website.replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0]
            params["domain"] = domain
        
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"   Lusha status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            # Extract phone if available
            phone = data.get("phoneNumber") or data.get("phone")
            if phone:
                return phone
            # Check for any phones in response
            if "data" in data:
                for item in data.get("data", []):
                    if item.get("phoneNumber"):
                        return item["phoneNumber"]
        elif resp.status_code == 429:
            print("   Rate limited")
            return "RATE_LIMIT"
        else:
            print(f"   Response: {resp.text[:200]}")
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
    
    # Get leads without phones - prioritize those with website
    cur.execute("""
        SELECT id, company_name, website_url, email 
        FROM leads 
        WHERE phone IS NULL AND company_name IS NOT NULL 
        ORDER BY website_url IS NOT NULL DESC
        LIMIT 15
    """)
    leads = cur.fetchall()
    print(f"Found {len(leads)} leads to enrich via Lusha")
    
    enriched = 0
    for lead_id, company, website, email in leads:
        print(f"Enriching {company} (site: {website})...")
        phone = enrich_with_lusha(company, website)
        if phone == "RATE_LIMIT":
            print("   Stopping - rate limit hit")
            break
        if phone:
            cur.execute("UPDATE leads SET phone = %s WHERE id = %s", (phone, lead_id))
            conn.commit()
            print(f"   ✓ Phone: {phone}")
            enriched += 1
        else:
            print("   ✗ No phone")
        time.sleep(0.5)  # Be nice to the API
    
    # Stats
    cur.execute("SELECT COUNT(*) FROM leads WHERE phone IS NOT NULL")
    total_with_phone = cur.fetchone()[0]
    print(f"\n=== ENRICHED {enriched} LEADS ===")
    print(f"=== TOTAL LEADS WITH PHONE: {total_with_phone} ===")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
