import os
import uuid
from supabase import create_client

def insert_leads():
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')
    supabase = create_client(url, key)

    leads = [
        {
            'id': str(uuid.uuid4()),
            'ghl_contact_id': 'WALKIN_' + str(uuid.uuid4())[:12],
            'full_name': 'Dr. Aleksander Precaj',
            'company_name': 'Aesthetic & Implant Dentistry',
            'website_url': 'https://aestheticimplantdentistry.com',
            'status': 'research_done',
            'niche': 'dentist',
            'address': '930 Marcum Road Suite 1, Lakeland, FL 33809',
            'email': 'yolanda@aestheticimplantdentistry.com',
            'phone': '8638597630',
            'lead_source': 'walk-in'
        },
        {
            'id': str(uuid.uuid4()),
            'ghl_contact_id': 'WALKIN_' + str(uuid.uuid4())[:12],
            'full_name': 'Mia',
            'company_name': 'Mia Spa & Massage',
            'website_url': 'https://miamassagespa.com',
            'status': 'research_done',
            'niche': 'massage',
            'address': '6723 US Hwy 98 N, Lakeland, FL 33809',
            'email': 'contact@miamassagespa.com',
            'phone': '8638151888',
            'lead_source': 'walk-in'
        },
        {
            'id': str(uuid.uuid4()),
            'ghl_contact_id': 'WALKIN_' + str(uuid.uuid4())[:12],
            'full_name': 'Keith Hargrove',
            'company_name': 'Keith Hargrove - State Farm',
            'website_url': 'https://keithhargrove.com',
            'status': 'research_done',
            'niche': 'insurance',
            'address': '6767 US Hwy 98 N Suite 3, Lakeland, FL 33809',
            'email': 'keith@keithhargrove.com',
            'phone': '8638584444',
            'lead_source': 'walk-in'
        },
        {
            'id': str(uuid.uuid4()),
            'ghl_contact_id': 'WALKIN_' + str(uuid.uuid4())[:12],
            'full_name': 'Northside Asian Kitchen',
            'company_name': 'Northside Asian Kitchen',
            'website_url': 'https://northsideasiankitchen.com',
            'status': 'research_done',
            'niche': 'restaurant',
            'address': '6737 US Hwy 98 N, Lakeland, FL 33809',
            'email': 'order@northsideasiankitchen.com',
            'phone': '8638532281',
            'lead_source': 'walk-in'
        }
    ]

    for lead in leads:
        try:
            # Remove UUID id if providing it causes issues with auto-gen
            # but usually it's better to provide one if id is not-null
            
            res = supabase.table("contacts_master").upsert(lead, on_conflict='ghl_contact_id').execute()
            if res.data:
                lead_id = res.data[0]['id']
                print(f"Upserted: {lead['company_name']} -> {lead_id}")
            else:
                print(f"Upsert returned no data for {lead['company_name']}")
        except Exception as e:
            print(f"Failed {lead['company_name']}: {e}")

if __name__ == "__main__":
    insert_leads()
