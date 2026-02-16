import os
import requests
import uuid

def insert_leads():
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }

    leads = [
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Dr. Aleksander Precaj',
            'company_name': 'Aesthetic & Implant Dentistry',
            'website_url': 'https://aestheticimplantdentistry.com',
            'status': 'research_done',
            'niche': 'dentist',
            'address': '930 Marcum Road Suite 1, Lakeland, FL 33809',
            'email': 'yolanda@aestheticimplantdentistry.com', # Placeholder for Yolanda
            'phone': '863-859-7630'
        },
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Mia',
            'company_name': 'Mia Spa & Massage',
            'website_url': 'https://miamassagespa.com',
            'status': 'research_done',
            'niche': 'massage',
            'address': '6723 US Hwy 98 N, Lakeland, FL 33809',
            'email': 'contact@miamassage.com',
            'phone': '863-815-1888'
        },
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Manager',
            'company_name': 'Florida Dermatology and Skin Cancer Centers',
            'website_url': 'https://fldscc.com',
            'status': 'research_done',
            'niche': 'dermatology',
            'address': '6743 US Hwy 98 N, Lakeland, FL 33809',
            'email': 'info@FLDSCC.com',
            'phone': '863-343-7546'
        },
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Keith Hargrove',
            'company_name': 'Keith Hargrove - State Farm',
            'website_url': 'https://keithhargrove.com',
            'status': 'research_done',
            'niche': 'insurance',
            'address': '6767 US Hwy 98 N Suite 3, Lakeland, FL 33809',
            'email': 'keith@keithhargrove.com',
            'phone': '863-858-4444'
        }
    ]

    for lead in leads:
        r = requests.post(f"{url}/rest/v1/contacts_master", headers=headers, json=lead)
        print(f"Insert {lead['company_name']}: {r.status_code}")
        if r.status_code >= 400:
            print(f"Error: {r.text}")

if __name__ == "__main__":
    insert_leads()
