"""
MANUS LEAD INGESTION v1
=======================
Ingests hiring-intent leads from Manus.im into contacts_master.
Tags them with source='manus' to trigger recruitment screener logic.
"""
import os
import json
import requests
from datetime import datetime, timezone

def ingest_manus_leads(leads_data: list):
    """
    Ingests a list of lead dicts.
    Expected format: [{"company_name": "...", "phone": "...", "website": "...", "job_role": "..."}]
    """
    from modules.database.supabase_client import get_supabase
    supabase = get_supabase()
    
    count = 0
    for lead in leads_data:
        email = lead.get("email", "")
        phone = lead.get("phone", "")
        company = lead.get("company_name", "Unknown Company")
        
        # Dedupe check
        existing = supabase.table("contacts_master").select("id").or_(f"company_name.ilike.{company},phone.eq.{phone}").execute()
        if not existing.data:
            record = {
                "company_name": company,
                "phone": phone,
                "email": email,
                "website_url": lead.get("website", ""),
                "status": "new",
                "source": "manus",
                "niche": lead.get("job_role", "Hiring Business"),
                "raw_research": json.dumps({
                    "job_role": lead.get("job_role"),
                    "manus_source": True,
                    "ingested_at": datetime.now(timezone.utc).isoformat()
                })
            }
            supabase.table("contacts_master").insert(record).execute()
            count += 1
            print(f"  📥 Ingested: {company} ({lead.get('job_role')})")
            
    return count

if __name__ == "__main__":
    # Sample data based on User's mention of 19 leads and earlier context
    # In practice, this would be fed by a JSON file or API.
    sample_leads = [
        {"company_name": "Reliable Heating & Air", "job_role": "HVAC Technician", "phone": "770-594-9969", "website": ""},
        {"company_name": "Coolray", "job_role": "Service Manager", "phone": "770-421-8400", "website": ""},
        {"company_name": "Acme USA", "job_role": "Operations Manager", "phone": "305-836-4800", "website": ""},
        {"company_name": "Bold City Heating & Air", "job_role": "Lead Installer", "phone": "904-379-1648", "website": ""},
        {"company_name": "The A/C Guy of Tampa Bay Inc.", "job_role": "Customer Service Rep", "phone": "727-286-3170", "website": ""},
        {"company_name": "Forest Air Conditioning & Heating", "job_role": "HVAC Mechanic", "phone": "727-865-6004", "website": ""},
        {"company_name": "Lakeside Heating, Cooling and Plumbing", "job_role": "Dispatcher", "phone": "813-444-9474", "website": ""},
        {"company_name": "Lakeland Air Conditioning", "job_role": "Helper", "phone": "863-859-4090", "website": ""},
        {"company_name": "AIM Service Group LLC", "job_role": "Sales Consultant", "phone": "813-833-2118", "website": ""},
        {"company_name": "Blue Star Air Conditioning", "job_role": "Office Admin", "phone": "321-204-0794", "website": ""},
        {"company_name": "Del-Air", "job_role": "Technician", "phone": "407-499-0774", "website": ""},
        {"company_name": "Ierna Air", "job_role": "Comfort Advisor", "phone": "813-578-7113", "website": ""},
        {"company_name": "McDevitt Air", "job_role": "Electrician", "phone": "877-692-9402", "website": ""},
        {"company_name": "Busby's Heating & Air Conditioning", "job_role": "Plumber", "phone": "706-664-0132", "website": ""},
        {"company_name": "Quality Air Conditioning Company", "job_role": "Project Manager", "phone": "954-504-6314", "website": ""},
        {"company_name": "Coolray Heating & Air Conditioning", "job_role": "HVAC Lead", "phone": "678-273-3016", "website": ""},
        {"company_name": "David Boston Heating & Cooling", "job_role": "Service Tech", "phone": "256-729-5665", "website": ""},
        {"company_name": "Mid South HVAC", "job_role": "Warehouse Manager", "phone": "256-453-8293", "website": ""},
        {"company_name": "Fort Worth Heat & Air", "job_role": "Field Supervisor", "phone": "817-800-0340", "website": ""}
    ]
    
    print(f"🚀 Starting Manus Ingestion for {len(sample_leads)} leads...")
    result = ingest_manus_leads(sample_leads)
    print(f"✅ Ingested {result} new leads.")
