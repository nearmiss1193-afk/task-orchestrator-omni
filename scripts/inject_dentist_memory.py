import os
from modules.database.supabase_client import get_supabase

def inject_dentist_memory():
    supabase = get_supabase()
    if not supabase:
        print("❌ Supabase client initialization failed.")
        return

    # Info to inject
    dentist_phone = "+18636443644" # Standard office line for Dr. Precaj
    dentist_email = "precaj@dentalexperience.com"
    dentist_name = "Dr. Aleksander Precaj"
    
    # Context summary for Maya
    context = {
        "contact_name": dentist_name,
        "email": dentist_email,
        "business_type": "Dentist (Aesthetic & Implant Dentistry)",
        "audit_status": "Digital Strike Sent (Feb 12)",
        "critical_finding": "Missing FDBR Privacy Policy (Florida Digital Bill of Rights)",
        "pagespeed_score": 42,
        "history": "Dan sent a full AI visibility audit on Feb 12. Most critical issue is the FDBR compliance gap. Maya should be aware of this if he calls back."
    }
    
    # Upsert into customer_memory
    try:
        res = supabase.table("customer_memory").upsert({
            "phone_number": dentist_phone,
            "customer_name": dentist_name,
            "context_summary": context,
            "updated_at": "now()"
        }, on_conflict="phone_number").execute()
        print(f"✅ Injected Dr. Precaj into Maya's memory (Phone: {dentist_phone})")
    except Exception as e:
        print(f"❌ Injection failed: {e}")

if __name__ == "__main__":
    inject_dentist_memory()
