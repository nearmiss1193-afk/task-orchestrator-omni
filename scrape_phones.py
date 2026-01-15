"""Scrape phone numbers directly from lead websites"""
import psycopg2
import requests
import re
import time

def extract_phone_from_website(url):
    """Scrape website for phone numbers"""
    if not url:
        return None
    
    # Ensure proper URL format
    if not url.startswith("http"):
        url = "https://" + url
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        
        if resp.status_code == 200:
            # Phone patterns
            patterns = [
                r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (xxx) xxx-xxxx or xxx-xxx-xxxx
                r'\+1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # +1 xxx-xxx-xxxx
                r'tel:[+]?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # tel: links
            ]
            
            text = resp.text
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Clean up the phone number
                    phone = matches[0].replace("tel:", "").strip()
                    # Standardize format
                    digits = re.sub(r'\D', '', phone)
                    if len(digits) == 10:
                        digits = "1" + digits
                    if len(digits) == 11 and digits.startswith("1"):
                        # Validate US area code (reject Canadian: 204,226,236,249,250,289,306,343,365,etc)
                        area_code = digits[1:4]
                        canadian_codes = ["204","226","236","249","250","289","306","343","365","367","403","416","418","431","437","438","450","506","514","519","548","579","581","587","604","613","639","647","705","709","778","780","782","807","819","825","867","873","902","905"]
                        if area_code in canadian_codes:
                            print("   Canadian number - skipped")
                            return None
                        # Reject fake patterns
                        if digits[1:] == "9999999999" or digits[1:] == "0000000000" or "555" in digits[4:7]:
                            print("   Fake number - skipped")
                            return None
                        return f"+{digits}"
            print("   No phone found on page")
        else:
            print(f"   HTTP {resp.status_code}")
    except requests.Timeout:
        print("   Timeout")
    except Exception as e:
        print(f"   Error: {str(e)[:50]}")
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
    
    # Get leads without phones but WITH website (including contacted ones we need to re-work)
    cur.execute("""
        SELECT id, company_name, website_url 
        FROM leads 
        WHERE phone IS NULL AND website_url IS NOT NULL AND website_url != ''
        LIMIT 50
    """)
    leads = cur.fetchall()
    print(f"Found {len(leads)} leads with websites to scrape")
    
    enriched = 0
    for lead_id, company, website in leads:
        print(f"Scraping {company}: {website}")
        phone = extract_phone_from_website(website)
        if phone:
            cur.execute("UPDATE leads SET phone = %s, status = 'new' WHERE id = %s", (phone, lead_id))
            conn.commit()
            print(f"   ✓ Found: {phone}")
            enriched += 1
        time.sleep(0.3)
    
    # Stats
    cur.execute("SELECT COUNT(*) FROM leads WHERE phone IS NOT NULL")
    total_with_phone = cur.fetchone()[0]
    print(f"\n=== SCRAPED {enriched} PHONES ===")
    print(f"=== TOTAL LEADS WITH PHONE: {total_with_phone} ===")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
