import os
import json
from modules.database.supabase_client import get_supabase
import json

def run_sync():
    supabase = get_supabase()
    if not supabase:
        print("❌ Supabase client failed (check env vars)")
        return

    # 1. INJECT DENTIST MEMORY
    dentist_phone = "+18636443644"
    dentist_email = "precaj@dentalexperience.com"
    dentist_name = "Dr. Aleksander Precaj"
    
    context = {
        "contact_name": dentist_name,
        "email": dentist_email,
        "business_type": "Dentist (Aesthetic & Implant Dentistry)",
        "audit_status": "Digital Strike Sent (Feb 12)",
        "critical_finding": "Missing FDBR Privacy Policy (Florida Digital Bill of Rights)",
        "pagespeed_score": 42,
        "history": "Dan sent a full AI visibility audit on Feb 12. Most critical issue is the FDBR compliance gap. Maya should be aware of this if he calls back."
    }
    
    try:
        # SURGICAL DELETE/INSERT
        supabase.table("customer_memory").delete().eq("phone_number", dentist_phone).execute()
        
        supabase.table("customer_memory").insert({
            "phone_number": dentist_phone,
            "customer_name": dentist_name,
            "context_summary": context 
        }).execute()
        print(f"✅ Injected {dentist_name} into Maya's memory")
    except Exception as e:
        print(f"❌ Dentist injection failed: {e}")

    # 2. INGEST 19 LEADS
    leads = [
        {"name": "Capernaum Medical Center for Kids", "url": "https://www.cmcwecare.com/", "owner": "Dr. Eric Vernier", "pain": "Overbooking, delays, lab results issues", "rating": 3.6, "reviews": 703},
        {"name": "Encompass Health Rehabilitation Hospital", "url": "https://www.encompasshealth.com/locations/lakeland-rehab", "owner": "Supriya Kumar", "pain": "Weekend phone coverage needed", "rating": 4.5, "reviews": 683},
        {"name": "New Beginnings High School", "url": "https://www.newbhs.net/", "owner": "Ivelis Cardona", "pain": "High volume of callers, data entry", "rating": "N/A", "reviews": "N/A"},
        {"name": "Vanguard Medical Care of Lakeland", "url": "https://www.vanguardmedcare.com/", "owner": "Dr. Chester Miltenberger", "pain": "After-hours support, weekend closures", "rating": 4.9, "reviews": 50},
        {"name": "Breezy Hills Rehabilitation", "url": "https://breezyhillsrehab.com/", "owner": "N/A", "pain": "Weekend phone coverage needed", "rating": 3.6, "reviews": 45},
        {"name": "The Family Dentist", "url": "https://www.thefamilydentist-lakeland.com/", "owner": "Dr. Mariela K. Lung", "pain": "Front desk administrative support", "rating": 4.7, "reviews": 14},
        {"name": "Doctor Today TLC", "url": "https://doctortodaytlc.com/", "owner": "Rekha Issar", "pain": "High patient call volume, scheduling", "rating": 3.7, "reviews": 421},
        {"name": "Sunburst Community Care", "url": "https://sunburstcommunitycare.com/", "owner": "Tyrus Hawkins", "pain": "Weekend phone coverage needed", "rating": 4.8, "reviews": 78},
        {"name": "Crunch Fitness", "url": "https://www.crunch.com/locations/lakeland", "owner": "Tony Scrimale", "pain": "Overcrowding peak hours, sales emphasis", "rating": 4.6, "reviews": 2138},
        {"name": "GEICO", "url": "https://www.geico.com/", "owner": "James Boley", "pain": "High-volume communication, logistical", "rating": 3.2, "reviews": "N/A"},
        {"name": "Courtyard by Marriott Lakeland", "url": "https://www.marriott.com/en-us/hotels/tpalk-courtyard-lakeland/overview/", "owner": "Trent White", "pain": "After-hours support, overnight staffing", "rating": 4.0, "reviews": 534},
        {"name": "Avakar Lakeland Hospitality", "url": "https://www.wyndhamhotels.com/hojo/lakeland-florida/howard-johnson-lakeland/overview", "owner": "Vivek Mistry", "pain": "High customer call volume, coordination", "rating": 3.5, "reviews": 1777},
        {"name": "Burnetti, P.A.", "url": "https://www.burnetti.com/", "owner": "Doug Burnetti", "pain": "Operational efficiency, IT coordination", "rating": 4.6, "reviews": 350},
        {"name": "Lex Construction LLC", "url": "https://lexconstructionllc.com/", "owner": "Vince Duarte", "pain": "Project management support", "rating": 5.0, "reviews": 2},
        {"name": "Polk Christian Preparatory School", "url": "https://christianprepschools.com/polk-christian-preparatory-school/", "owner": "Jessica Tapia", "pain": "Demanding administrative tasks", "rating": 5.0, "reviews": 15},
        {"name": "Allied Crawford (Lakeland), Inc.", "url": "https://crawfordsteel.com/", "owner": "Sidney Spiegel", "pain": "Slow service, customer service issues", "rating": 2.7, "reviews": 38},
        {"name": "Ferrera Tooling Inc", "url": "https://www.ferreratooling.com/", "owner": "Brian Herrera", "pain": "Social media and admin support", "rating": 5.0, "reviews": 4},
        {"name": "Florida Southern College", "url": "https://www.flsouthern.edu/", "owner": "Sara Terrell", "pain": "Administrative support, operational efficiency", "rating": 4.4, "reviews": 193},
        {"name": "AdventHealth Primary Care+", "url": "N/A", "owner": "N/A", "pain": "Front desk concierge needs", "rating": "N/A", "reviews": "N/A"}
    ]
    
    count = 0
    for l in leads:
        try:
            # Simple deduplication
            exists = supabase.table("contacts_master").select("id").ilike("company_name", f"%{l['name']}%").limit(1).execute()
            if not exists.data:
                supabase.table("contacts_master").insert({
                    "company_name": l['name'],
                    "website_url": l['url'],
                    "full_name": l['owner'],
                    "status": "new",
                    "source": "hiring_trigger",
                    "notes": f"Hiring Trigger: {l['pain']} | Rating: {l['rating']} | Reviews: {l['reviews']}"
                }).execute()
                count += 1
        except Exception as e:
            print(f"⚠️ Failed to ingest {l['name']}: {e}")
            
    print(f"✅ Ingested {count} new Hiring Trigger leads")

    # Final Verification
    total = supabase.table("contacts_master").select("id", count="exact").ilike("source", "hiring_trigger").execute()
    print(f"📊 Total Hiring Trigger leads in DB: {total.count}")

if __name__ == "__main__":
    run_sync()
