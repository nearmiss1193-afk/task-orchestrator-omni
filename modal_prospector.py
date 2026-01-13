"""
MODAL PROSPECTOR - Cloud-based lead generation
Uses Apollo API for prospecting (not browser automation)
Runs on scheduled intervals in the cloud
"""
import modal

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "requests", "supabase", "python-dotenv", "fastapi"
)

app = modal.App("empire-prospector")
VAULT = modal.Secret.from_name("empire-vault")

# Target niches for prospecting
NICHES = [
    {"keywords": "HVAC contractor", "location": "Florida", "employees": "1,10"},
    {"keywords": "Plumbing services", "location": "Texas", "employees": "1,10"},
    {"keywords": "Roofing company", "location": "Georgia", "employees": "1,10"},
    {"keywords": "Electrical contractor", "location": "California", "employees": "11,50"},
    {"keywords": "HVAC repair", "location": "Ohio", "employees": "1,10"},
]

@app.function(image=image, secrets=[VAULT], timeout=600)
def prospect_batch(niche: dict):
    """Find leads for a specific niche using Apollo API"""
    import requests
    import os
    from datetime import datetime
    
    apollo_key = os.environ.get("APOLLO_API_KEY")
    if not apollo_key:
        return {"status": "error", "reason": "no_apollo_key"}
    
    print(f"[PROSPECTOR] Searching: {niche['keywords']} in {niche['location']}")
    
    try:
        resp = requests.post(
            "https://api.apollo.io/v1/mixed_companies/search",
            headers={"Content-Type": "application/json"},
            json={
                "api_key": apollo_key,
                "q_keywords": niche["keywords"],
                "organization_locations": [niche["location"]],
                "organization_num_employees_ranges": [niche.get("employees", "1,50")],
                "per_page": 25
            },
            timeout=60
        )
        
        if resp.status_code == 429:
            print("[PROSPECTOR] Rate limited - backing off")
            return {"status": "rate_limited", "niche": niche["keywords"]}
        
        if resp.ok:
            data = resp.json()
            companies = data.get("organizations", [])
            print(f"[PROSPECTOR] Found {len(companies)} companies")
            
            # Save to Supabase
            leads_saved = save_to_supabase(companies)
            
            return {
                "status": "success",
                "niche": niche["keywords"],
                "found": len(companies),
                "saved": leads_saved
            }
        else:
            return {"status": "error", "code": resp.status_code}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}


def save_to_supabase(companies: list):
    """Save leads to Supabase database"""
    import os
    from supabase import create_client
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("[SUPABASE] Missing credentials")
        return 0
    
    try:
        sb = create_client(url, key)
        saved = 0
        
        for company in companies:
            lead_data = {
                "company_name": company.get("name", "Unknown"),
                "website_url": company.get("website_url"),
                "phone": company.get("phone"),
                "city": company.get("city"),
                "state": company.get("state"),
                "industry": company.get("industry"),
                "employees": company.get("estimated_num_employees"),
                "status": "new",
                "source": "apollo_cloud"
            }
            
            # Check if exists
            existing = sb.table("leads").select("id").eq("company_name", lead_data["company_name"]).execute()
            
            if not existing.data:
                sb.table("leads").insert(lead_data).execute()
                saved += 1
                print(f"[SAVED] {lead_data['company_name']}")
        
        return saved
    except Exception as e:
        print(f"[SUPABASE ERROR] {e}")
        return 0


@app.function(image=image, secrets=[VAULT], schedule=modal.Period(hours=2))
def scheduled_prospect():
    """Run prospecting every 2 hours automatically"""
    import random
    from datetime import datetime
    
    print(f"[SCHEDULED] Prospecting run at {datetime.utcnow().isoformat()}")
    
    # Pick 2 random niches to avoid hitting rate limits
    selected = random.sample(NICHES, min(2, len(NICHES)))
    
    results = []
    for niche in selected:
        result = prospect_batch.remote(niche)
        results.append(result)
    
    # Send summary to owner
    send_prospect_summary(results)
    
    return {"status": "completed", "niches_processed": len(selected)}


def send_prospect_summary(results: list):
    """Send email summary of prospecting results"""
    import requests
    
    GHL_EMAIL = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8"
    
    total_found = sum(r.get("found", 0) for r in results if isinstance(r, dict))
    total_saved = sum(r.get("saved", 0) for r in results if isinstance(r, dict))
    
    html = f"""
    <h2>Cloud Prospector Report</h2>
    <p>Leads Found: <b>{total_found}</b></p>
    <p>Leads Saved: <b>{total_saved}</b></p>
    <p>Status: All systems operational</p>
    """
    
    try:
        requests.post(GHL_EMAIL, json={
            "email": "owner@aiserviceco.com",
            "from_name": "Empire Prospector",
            "from_email": "system@aiserviceco.com",
            "subject": f"[CLOUD] {total_saved} new leads found",
            "html_body": html
        }, timeout=15)
    except:
        pass


@app.function(image=image, secrets=[VAULT])
@modal.web_endpoint(method="POST")
def trigger_prospect(payload: dict):
    """Manually trigger prospecting via API"""
    niche = payload.get("niche", {"keywords": "HVAC contractor", "location": "Florida"})
    result = prospect_batch.remote(niche)
    return result


@app.function(image=image)
@modal.web_endpoint(method="GET")
def health():
    """Health check"""
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "empire-prospector",
        "time": datetime.utcnow().isoformat(),
        "schedule": "every 2 hours"
    }


if __name__ == "__main__":
    print("Deploy: modal deploy modal_prospector.py")
