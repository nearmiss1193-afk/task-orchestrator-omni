"""
Enrichment Worker - Runs website audits on new leads
Runs every 2 hours via Railway Cron
"""
import os
import time
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Import shared clients
from supabase_client import get_client, get_enrichable_leads, update_lead_status

# PageSpeed API
PAGESPEED_API_KEY = os.getenv("GOOGLE_PAGESPEED_API_KEY", "")


def run_pagespeed_audit(url: str) -> dict:
    """Run Google PageSpeed Insights audit on a URL"""
    if not url:
        return {"error": "No URL provided"}
    
    # Ensure URL has protocol
    if not url.startswith("http"):
        url = f"https://{url}"
    
    api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "category": ["performance", "accessibility", "best-practices", "seo"],
        "strategy": "mobile"
    }
    if PAGESPEED_API_KEY:
        params["key"] = PAGESPEED_API_KEY
    
    try:
        with httpx.Client(timeout=60) as client:
            response = client.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            lighthouse = data.get("lighthouseResult", {})
            categories = lighthouse.get("categories", {})
            
            scores = {
                "performance": int(categories.get("performance", {}).get("score", 0) * 100),
                "accessibility": int(categories.get("accessibility", {}).get("score", 0) * 100),
                "best_practices": int(categories.get("best-practices", {}).get("score", 0) * 100),
                "seo": int(categories.get("seo", {}).get("score", 0) * 100)
            }
            
            # Overall score (average)
            scores["overall"] = sum(scores.values()) // 4
            
            return scores
            
    except Exception as e:
        return {"error": str(e), "overall": 0}


def check_ssl(url: str) -> bool:
    """Check if a website has valid SSL certificate"""
    if not url:
        return False
    
    # Ensure HTTPS
    https_url = url.replace("http://", "https://")
    if not https_url.startswith("https"):
        https_url = f"https://{https_url}"
    
    try:
        with httpx.Client(timeout=10, verify=True) as client:
            response = client.head(https_url)
            return response.status_code < 400
    except:
        return False


def check_forms(url: str) -> bool:
    """Check if website has contact forms"""
    if not url:
        return False
    
    try:
        with httpx.Client(timeout=15) as client:
            response = client.get(url)
            html = response.text.lower()
            
            # Look for form indicators
            form_indicators = [
                "<form",
                "contact-form",
                "contactform",
                'type="submit"',
                "name=\"email\"",
                "name='email'"
            ]
            return any(indicator in html for indicator in form_indicators)
    except:
        return False


def check_legal_compliance(url: str) -> dict:
    """Check for privacy policy, terms of service, etc."""
    if not url:
        return {"privacy_policy": False, "terms": False}
    
    try:
        with httpx.Client(timeout=15) as client:
            response = client.get(url)
            html = response.text.lower()
            
            return {
                "privacy_policy": "privacy" in html or "privacy-policy" in html,
                "terms": "terms" in html or "terms-of-service" in html
            }
    except:
        return {"privacy_policy": False, "terms": False}


def determine_traffic_light(scores: dict, ssl: bool, has_forms: bool) -> str:
    """Determine overall traffic light status: RED, YELLOW, or GREEN"""
    issues = 0
    
    # Performance < 50 = major issue
    if scores.get("overall", 0) < 50:
        issues += 2
    elif scores.get("overall", 0) < 70:
        issues += 1
    
    # No SSL = major issue
    if not ssl:
        issues += 2
    
    # No forms = issue
    if not has_forms:
        issues += 1
    
    # SEO < 70 = issue
    if scores.get("seo", 0) < 70:
        issues += 1
    
    if issues >= 3:
        return "RED"
    elif issues >= 1:
        return "YELLOW"
    return "GREEN"


def enrich_lead(lead: dict) -> dict:
    """Run full enrichment on a single lead"""
    website = lead.get("website_url", "")
    
    # If no website, mark as RED immediately (hot prospect)
    if not website:
        return {
            "pagespeed_score": None,
            "ssl_status": False,
            "forms_present": False,
            "legal_compliance": False,
            "traffic_light": "RED",
            "fit_score": 90,  # Very hot - no website at all
            "status": "enriched"
        }
    
    print(f"   🔍 Auditing: {website}")
    
    # Run audits
    pagespeed = run_pagespeed_audit(website)
    ssl = check_ssl(website)
    has_forms = check_forms(website)
    legal = check_legal_compliance(website)
    
    # Determine traffic light
    traffic_light = determine_traffic_light(pagespeed, ssl, has_forms)
    
    # Calculate fit score based on issues
    fit_score = 50
    if traffic_light == "RED":
        fit_score = 85
    elif traffic_light == "YELLOW":
        fit_score = 70
    else:
        fit_score = 40  # GREEN = less urgent need
    
    return {
        "pagespeed_score": pagespeed.get("overall"),
        "pagespeed_performance": pagespeed.get("performance"),
        "pagespeed_seo": pagespeed.get("seo"),
        "ssl_status": ssl,
        "forms_present": has_forms,
        "legal_compliance": legal.get("privacy_policy", False),
        "traffic_light": traffic_light,
        "fit_score": fit_score,
        "status": "enriched",
        "enriched_at": datetime.utcnow().isoformat()
    }


def run_enrichment_cycle():
    """Main enrichment cycle - run this every 2 hours"""
    print(f"\n{'='*60}")
    print(f"📊 ENRICHMENT WORKER - {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # Get leads that need enrichment
    leads = get_enrichable_leads(limit=25)  # Process 25 at a time
    print(f"📋 Found {len(leads)} leads to enrich\n")
    
    enriched_count = 0
    red_count = 0
    yellow_count = 0
    green_count = 0
    
    for lead in leads:
        print(f"\n🏢 {lead.get('business_name', 'Unknown')}")
        
        try:
            enrichment_data = enrich_lead(lead)
            update_lead_status(lead["id"], "enriched", enrichment_data)
            enriched_count += 1
            
            traffic_light = enrichment_data.get("traffic_light", "UNKNOWN")
            if traffic_light == "RED":
                red_count += 1
                print(f"   🔴 RED - Hot prospect!")
            elif traffic_light == "YELLOW":
                yellow_count += 1
                print(f"   🟡 YELLOW - Needs work")
            else:
                green_count += 1
                print(f"   🟢 GREEN - Website OK")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Rate limiting
        time.sleep(3)
    
    print(f"\n{'='*60}")
    print(f"📈 ENRICHMENT RESULTS:")
    print(f"   🔴 RED (hot):    {red_count}")
    print(f"   🟡 YELLOW:       {yellow_count}")
    print(f"   🟢 GREEN:        {green_count}")
    print(f"   Total enriched:  {enriched_count}")
    print(f"{'='*60}\n")
    
    return {
        "enriched": enriched_count,
        "red": red_count,
        "yellow": yellow_count,
        "green": green_count
    }


if __name__ == "__main__":
    run_enrichment_cycle()
