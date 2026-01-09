# diagnose_failed_leads.py - Analyze why leads failed initialization
import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def main():
    s = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get all failed leads
    failed = s.table('leads').select('*').eq('status', 'failed_init').execute().data
    
    with open("failed_leads_analysis.txt", "w", encoding="utf-8") as f:
        f.write(f"=== FAILED LEADS ANALYSIS ({len(failed)} total) ===\n\n")
        
        # Group by error type
        issues = {
            "no_phone": [],
            "invalid_format": [],
            "missing_fields": [],
            "other": []
        }
        
        for lead in failed:
            phone = lead.get('phone') or lead.get('phone_number') or lead.get('phoneNumber')
            company = lead.get('company') or lead.get('business_name') or lead.get('name')
            
            if not phone:
                issues["no_phone"].append((company, lead))
            elif not phone.startswith('+') and not phone.startswith('1'):
                issues["invalid_format"].append((company, phone, lead))
            elif len(phone.replace('+','').replace('-','').replace(' ','').replace('(','').replace(')','')) < 10:
                issues["invalid_format"].append((company, phone, lead))
            else:
                issues["other"].append((company, phone, lead))
        
        f.write(f"NO PHONE NUMBER: {len(issues['no_phone'])}\n")
        for item in issues['no_phone'][:5]:
            f.write(f"  - Company: {item[0]}\n")
            f.write(f"    Full record keys: {list(item[1].keys())}\n")
        
        f.write(f"\nINVALID FORMAT: {len(issues['invalid_format'])}\n")
        for item in issues['invalid_format'][:5]:
            f.write(f"  - Company: {item[0]} | Phone: '{item[1]}'\n")
        
        f.write(f"\nOTHER ISSUES: {len(issues['other'])}\n")
        for item in issues['other'][:5]:
            f.write(f"  - Company: {item[0]} | Phone: '{item[1]}'\n")
        
        # Show a sample full record
        if failed:
            f.write(f"\n=== SAMPLE FULL RECORD ===\n")
            sample = failed[0]
            for k, v in sample.items():
                f.write(f"  {k}: {v}\n")
    
    print("Analysis written to failed_leads_analysis.txt")

if __name__ == "__main__":
    main()
