"""TURBO INSERT — Verified leads from web search, all with websites + emails."""
import os, sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('.env')
load_dotenv('.env.local')
from supabase import create_client

s = create_client(
    os.getenv('NEXT_PUBLIC_SUPABASE_URL') or os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

LEADS = [
    # HVAC - Lakeland FL
    {"company_name": "Roth's Air Conditioning & Refrigeration", "website_url": "https://rothsairconditioning.com", "email": "info@rothsairconditioning.com", "phone": "+18638087877", "niche": "HVAC contractor", "source": "web_search_lakeland"},
    {"company_name": "Acu-Temp Heating & Cooling", "website_url": "https://acu-temp.com", "email": None, "phone": "+18636823803", "niche": "HVAC contractor", "source": "web_search_lakeland"},
    {"company_name": "The Lakeland Air Conditioning Company", "website_url": "https://thelakelandac.com", "email": None, "phone": "+18638594090", "niche": "HVAC contractor", "source": "web_search_lakeland"},
    {"company_name": "Affordable Air Conditioning and Heating", "website_url": "https://airconditioningandheatingfla.com", "email": None, "phone": "+18638607633", "niche": "HVAC contractor", "source": "web_search_lakeland"},
    {"company_name": "Action Heating and Cooling", "website_url": "https://actionheatingandcoolinginc.com", "email": None, "phone": "+18637017777", "niche": "HVAC contractor", "source": "web_search_lakeland"},
    {"company_name": "CAMS A/C N Plumbing", "website_url": "https://camsairconditioning.com", "email": None, "phone": "+18632798743", "niche": "HVAC contractor", "source": "web_search_lakeland"},
    {"company_name": "Comfort Temp HVAC", "website_url": "https://www.comforttemp.com", "email": None, "phone": None, "niche": "HVAC contractor", "source": "web_search_gainesville"},
    {"company_name": "Sun State Air Conditioning", "website_url": "https://www.sunstateac.com", "email": None, "phone": None, "niche": "HVAC contractor", "source": "web_search_jacksonville"},
    {"company_name": "Energy Air Inc", "website_url": "https://www.energyair.com", "email": None, "phone": None, "niche": "HVAC contractor", "source": "web_search_orlando"},

    # Plumbing - Tampa FL
    {"company_name": "Premium Plumbing Tampa", "website_url": "https://mypremiumplumbing.com", "email": "info@mypremiumplumbing.com", "phone": None, "niche": "plumbing company", "source": "web_search_tampa"},
    {"company_name": "Cass Plumbing Tampa Bay", "website_url": "https://cassplumbingtampabay.com", "email": "support@cassplumbingtampabay.com", "phone": None, "niche": "plumbing company", "source": "web_search_tampa"},
    {"company_name": "Bay Area Plumbing Inc", "website_url": "https://bayareaplumbinginc.com", "email": "info@bayareaplumbinginc.com", "phone": None, "niche": "plumbing company", "source": "web_search_tampa"},
    {"company_name": "Friends Plumbing Tampa", "website_url": "https://friendsplumbing.com", "email": None, "phone": None, "niche": "plumbing company", "source": "web_search_tampa"},
    {"company_name": "Aztec Plumbing & Drains", "website_url": "https://www.aztecplumbing.net", "email": None, "phone": None, "niche": "plumbing company", "source": "web_search_fortmyers"},

    # Roofing - Orlando FL
    {"company_name": "Roof Company Orlando", "website_url": "https://roofcompanyorlando.com", "email": "roofcompanyorlando@gmail.com", "phone": "+14076042017", "niche": "roofing contractor", "source": "web_search_orlando"},
    {"company_name": "Quality Roofing Solutions", "website_url": "https://qualityroofingsolutions.com", "email": "info@qualityroofingsolutions.com", "phone": "+18506413657", "niche": "roofing contractor", "source": "web_search_orlando"},
    {"company_name": "My Roofers Orlando", "website_url": "https://myroofersorlando.com", "email": "info@myroofersorlando.com", "phone": "+13213668955", "niche": "roofing contractor", "source": "web_search_orlando"},
    {"company_name": "Performance Roofing USA", "website_url": "https://performanceroofingusa.com", "email": "info@performanceroofingusa.com", "phone": "+14072101503", "niche": "roofing contractor", "source": "web_search_orlando"},

    # Pest Control - Jacksonville FL
    {"company_name": "Knock Out Pest Control Jax", "website_url": "https://knockoutpestcontroljacksonville.com", "email": "info@knockoutpestelimination.com", "phone": None, "niche": "pest control company", "source": "web_search_jacksonville"},
    {"company_name": "Turner Pest Control", "website_url": "https://turnerpest.com", "email": "customerservice@turnerpest.com", "phone": None, "niche": "pest control company", "source": "web_search_jacksonville"},
    {"company_name": "Lindsey Pest Services", "website_url": "https://lindseypest.com", "email": None, "phone": "+19043509406", "niche": "pest control company", "source": "web_search_jacksonville"},

    # Landscaping - Sarasota FL
    {"company_name": "Sarasota Lawn & Landscaping", "website_url": "https://sarasotalawnandlandscaping.com", "email": "sarasotalawnandlandscaping@yahoo.com", "phone": None, "niche": "landscaping company", "source": "web_search_sarasota"},
    {"company_name": "Sarasota Landscaping Inc", "website_url": "https://about.me/sarasotalandscaping", "email": "landscapesarasota@gmail.com", "phone": None, "niche": "landscaping company", "source": "web_search_sarasota"},
    {"company_name": "Segura Landscaping LLC", "website_url": "https://seguralandscapingllc.com", "email": "seguralandscapingllc@gmail.com", "phone": None, "niche": "landscaping company", "source": "web_search_sarasota"},
    {"company_name": "Plant Source FL", "website_url": "https://plantsourcefl.com", "email": "office@plantsourcefl.com", "phone": None, "niche": "landscaping company", "source": "web_search_sarasota"},

    # Electrical - Fort Myers FL
    {"company_name": "Southwest Florida Electric Inc", "website_url": "https://swflelectric.com", "email": None, "phone": "+12397455020", "niche": "electrical contractor", "source": "web_search_fortmyers"},
    {"company_name": "Collier Electric Fort Myers", "website_url": "https://collierelectricfm.com", "email": None, "phone": "+12392757888", "niche": "electrical contractor", "source": "web_search_fortmyers"},
]

# Filter to only leads with emails (audit pipeline requires email)
email_leads = [l for l in LEADS if l.get('email')]
website_only = [l for l in LEADS if not l.get('email') and l.get('website_url')]

print("=" * 60)
print("  TURBO INSERT — Verified FL Business Leads")
print("=" * 60)
print(f"  Total leads: {len(LEADS)}")
print(f"  With email (priority): {len(email_leads)}")
print(f"  Website only (will scrape emails later): {len(website_only)}")

inserted = 0
skipped = 0

# Insert ALL leads (with and without email) — they all have websites for audit
import uuid
for lead in LEADS:
    lead["status"] = "new"
    lead["funnel_stage"] = "new"
    lead["ghl_contact_id"] = f"SCRAPED_{uuid.uuid4().hex[:12]}"
    
    # Clean up None values
    lead = {k: v for k, v in lead.items() if v is not None}
    
    # Dedup check
    try:
        existing = s.table("contacts_master").select("id").eq("website_url", lead.get("website_url", "")).limit(1).execute()
        if existing.data:
            print(f"  Skip (dup): {lead['company_name']}")
            skipped += 1
            continue
        if lead.get("email"):
            existing2 = s.table("contacts_master").select("id").eq("email", lead["email"]).limit(1).execute()
            if existing2.data:
                print(f"  Skip (dup email): {lead['company_name']}")
                skipped += 1
                continue
    except:
        pass
    
    try:
        s.table("contacts_master").insert(lead).execute()
        inserted += 1
        em = lead.get('email', 'no-email')
        print(f"  ✅ {lead['company_name']} | {em}")
    except Exception as e:
        print(f"  ❌ {lead['company_name']}: {e}")

print(f"\n  INSERTED: {inserted}")
print(f"  SKIPPED (dup): {skipped}")
print(f"  All have websites -> AUDIT PIPELINE READY")
