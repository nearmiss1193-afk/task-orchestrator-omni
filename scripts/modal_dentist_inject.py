import modal
from deploy import image, VAULT

app = modal.App("dentist-sync")

@app.function(image=image, secrets=[VAULT])
def inject_dentist():
    from modules.database.supabase_client import get_supabase
    import json
    
    supabase = get_supabase()
    if not supabase:
        print("❌ Supabase client failed")
        return

    ph = "+18636443644"
    context = {
        "contact_name": "Dr. Aleksander Precaj",
        "email": "precaj@dentalexperience.com",
        "business_type": "Dentist (Aesthetic & Implant Dentistry)",
        "audit_status": "Digital Strike Sent (Feb 12)",
        "critical_finding": "Missing FDBR Privacy Policy (Florida Digital Bill of Rights)",
        "pagespeed_score": 42,
        "history": "Dan sent a full AI visibility audit on Feb 12. Most critical issue is the FDBR compliance gap. Maya should be aware of this if he calls back."
    }
    
    try:
        # Delete then Insert to be 100% sure
        supabase.table("customer_memory").delete().eq("phone_number", ph).execute()
        supabase.table("customer_memory").insert({
            "phone_number": ph,
            "customer_name": "Dr. Aleksander Precaj",
            "context_summary": context
        }).execute()
        print(f"✅ SUCCESSFULLY INJECTED DENTIST MEMORY")
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    with app.run():
        inject_dentist.remote()
