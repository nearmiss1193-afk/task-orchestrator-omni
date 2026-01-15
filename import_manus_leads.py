"""Manual HVAC Lead Import - for Manus campaign follow-up calls
User should paste leads from Manus CSV here, or save CSV and run this.
"""
import psycopg2
import csv
import os

# Direct DB connection
conn = psycopg2.connect(
    host="db.rzcpfwkygdvoshtwxncs.supabase.co",
    port=5432, database="postgres", user="postgres", password="Inez11752990@"
)
cur = conn.cursor()

# Check if CSV file exists
csv_path = "manus_hvac.csv"

# Sample leads - USER CAN REPLACE THIS WITH ACTUAL MANUS DATA
# Format: company_name, phone, email, city, state
sample_leads = [
    # PASTE MANUS LEADS HERE - format:
    # ("Company Name", "+1XXXXXXXXXX", "email@domain.com", "City", "State"),
]

def import_leads(leads):
    added = 0
    for lead in leads:
        company, phone, email, city, state = lead
        
        # Check duplicate
        cur.execute("SELECT id FROM leads WHERE company_name = %s", (company,))
        if cur.fetchone():
            print(f"  Skip (exists): {company}")
            continue
        
        # Insert
        cur.execute("""
            INSERT INTO leads (company_name, phone, email, city, state, industry, status, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (company, phone, email, city, state, "HVAC", "new", "manus_campaign"))
        conn.commit()
        print(f"  ✅ Added: {company}")
        added += 1
    
    print(f"\n=== IMPORTED {added} HVAC LEADS ===")
    return added

def import_from_csv():
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        print("Please save Manus CSV as 'manus_hvac.csv' and run again")
        return 0
    
    leads = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Adjust column names based on actual CSV
            company = row.get('Company Name', row.get('company', row.get('name', '')))
            phone = row.get('Phone', row.get('phone', ''))
            email = row.get('Email', row.get('email', ''))
            city = row.get('City', row.get('city', ''))
            state = row.get('State', row.get('state', ''))
            
            if company and phone:
                leads.append((company, phone, email, city, state))
    
    print(f"Found {len(leads)} leads in CSV")
    return import_leads(leads)

if __name__ == "__main__":
    print("=== MANUS HVAC LEAD IMPORTER ===")
    
    if sample_leads:
        import_leads(sample_leads)
    else:
        import_from_csv()
    
    # Show total ready leads
    cur.execute("SELECT COUNT(*) FROM leads WHERE status = 'new' AND phone IS NOT NULL")
    print(f"\nTotal NEW leads with phone: {cur.fetchone()[0]}")
    
    cur.close()
    conn.close()
