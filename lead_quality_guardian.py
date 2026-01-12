"""
LEAD QUALITY GUARDIAN - Self-Healing Enrichment System
======================================================
Automatically validates, enriches, and repairs lead data before campaigns.
Ensures no calls are wasted on invalid/fake phone numbers.

SOP: This runs BEFORE cloud_multi_touch to guarantee quality.
"""
import os
import re
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
MANUS_API_KEY = os.getenv("MANUS_API_KEY")  # Backup for Grok research

# Phone validation constants
INVALID_EXCHANGES = ['555']  # Fake phone prefixes
REQUIRED_LENGTH = 10


def validate_phone(phone_str):
    """
    Validate a phone number.
    Returns: (is_valid, cleaned_number, issue)
    """
    if not phone_str:
        return False, None, "missing"
    
    # Clean to digits only
    cleaned = re.sub(r'\D', '', str(phone_str))
    
    # Must be 10+ digits
    if len(cleaned) < 10:
        return False, cleaned, "too_short"
    
    # Extract exchange (NXX in NPA-NXX-XXXX format)
    # For 10 digits: positions 3-5 are the exchange
    if len(cleaned) >= 10:
        exchange = cleaned[-7:-4]
        if exchange in INVALID_EXCHANGES:
            return False, cleaned, "fake_555"
    
    return True, cleaned[-10:], None


def enrich_with_apollo(company_name, city=None):
    """
    Enrich company with Apollo.io API.
    Returns decision maker with REAL phone and email.
    """
    if not APOLLO_API_KEY:
        return None, "Apollo API key not configured"
    
    url = "https://api.apollo.io/v1/mixed_people/search"
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_API_KEY
    }
    
    # Search for owner/decision maker
    payload = {
        "q_organization_name": company_name,
        "person_titles": ["Owner", "CEO", "President", "General Manager"],
        "page": 1,
        "per_page": 3
    }
    
    if city:
        payload["person_locations"] = [city]
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and data.get("people"):
            for person in data["people"]:
                phone_numbers = person.get("phone_numbers", [])
                phone = phone_numbers[0].get("raw_number") if phone_numbers else None
                
                if phone:
                    is_valid, cleaned, issue = validate_phone(phone)
                    if is_valid:
                        return {
                            "name": person.get("name"),
                            "email": person.get("email"),
                            "phone": f"+1{cleaned}",
                            "title": person.get("title"),
                            "linkedin": person.get("linkedin_url"),
                            "source": "apollo"
                        }, None
            
            # If we got people but no valid phones
            return None, "no_valid_phone_found"
        
        return None, data.get("message", "no_results")
    
    except Exception as e:
        return None, str(e)


def enrich_with_hunter(domain, first_name=None, last_name=None):
    """
    Find email for a person at a company domain using Hunter.io.
    """
    if not HUNTER_API_KEY:
        return None, "Hunter API key not configured"
    
    url = "https://api.hunter.io/v2/email-finder"
    params = {
        "domain": domain,
        "api_key": HUNTER_API_KEY
    }
    
    if first_name:
        params["first_name"] = first_name
    if last_name:
        params["last_name"] = last_name
    
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if response.status_code == 200 and data.get("data", {}).get("email"):
            return {
                "email": data["data"]["email"],
                "score": data["data"].get("score", 0),
                "source": "hunter"
            }, None
        
        return None, "email_not_found"
    
    except Exception as e:
        return None, str(e)


def validate_and_repair_leads(limit=20):
    """
    Main function: Validate all leads and auto-repair invalid ones.
    
    SOP Steps:
    1. Get leads with status 'new' or 'processing_email'
    2. Validate phone numbers
    3. If invalid: Try Apollo enrichment
    4. If still invalid: Mark as 'needs_manual_review'
    5. Log all actions for monitoring
    """
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 70)
    print("🛡️ LEAD QUALITY GUARDIAN - Self-Healing Enrichment")
    print(f"   Time: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Get leads to validate
    result = client.table("leads").select("*").in_(
        "status", ["new", "processing_email"]
    ).limit(limit).execute()
    
    leads = result.data
    print(f"\n📋 Processing {len(leads)} leads...")
    
    stats = {
        "total": len(leads),
        "valid": 0,
        "enriched": 0,
        "failed": 0,
        "skipped": 0
    }
    
    for lead in leads:
        lead_id = lead.get("id")
        company = lead.get("company_name", "Unknown")
        city = lead.get("city")
        
        # Extract existing phone
        phone = lead.get("phone", "")
        agent_research = lead.get("agent_research", {})
        if isinstance(agent_research, str):
            try:
                agent_research = json.loads(agent_research)
            except:
                agent_research = {}
        
        research_phone = agent_research.get("phone", "") if agent_research else ""
        current_phone = phone or research_phone
        
        # Validate
        is_valid, cleaned, issue = validate_phone(current_phone)
        
        if is_valid:
            print(f"   ✅ {company[:35]:35} | +1{cleaned} | VALID")
            stats["valid"] += 1
            continue
        
        # Need enrichment
        print(f"   🔧 {company[:35]:35} | {current_phone or 'MISSING':15} | {issue} → Enriching...")
        
        # Try Apollo first
        enriched, error = enrich_with_apollo(company, city)
        
        if enriched:
            # Update lead with enriched data
            update_data = {
                "phone": enriched["phone"],
                "owner_name": enriched.get("name"),
                "agent_research": json.dumps({
                    **agent_research,
                    "enriched_phone": enriched["phone"],
                    "enriched_email": enriched.get("email"),
                    "enriched_name": enriched.get("name"),
                    "enriched_title": enriched.get("title"),
                    "enrichment_source": "apollo",
                    "enriched_at": datetime.now().isoformat()
                })
            }
            
            if enriched.get("email"):
                update_data["email"] = enriched["email"]
            
            client.table("leads").update(update_data).eq("id", lead_id).execute()
            
            print(f"      ✅ ENRICHED: {enriched['phone']} | {enriched.get('name', 'N/A')}")
            stats["enriched"] += 1
        else:
            # Mark for manual review
            client.table("leads").update({
                "status": "needs_enrichment",
                "agent_research": json.dumps({
                    **agent_research,
                    "enrichment_failed": True,
                    "enrichment_error": error,
                    "enrichment_attempted": datetime.now().isoformat()
                })
            }).eq("id", lead_id).execute()
            
            print(f"      ❌ FAILED: {error}")
            stats["failed"] += 1
    
    # Log to system_logs
    client.table("system_logs").insert({
        "level": "INFO",
        "event_type": "LEAD_QUALITY_CHECK",
        "message": f"Lead quality guardian: {stats['enriched']} enriched, {stats['valid']} valid, {stats['failed']} failed",
        "metadata": {
            **stats,
            "timestamp": datetime.now().isoformat()
        }
    }).execute()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print(f"   Total processed: {stats['total']}")
    print(f"   Already valid:   {stats['valid']}")
    print(f"   Enriched:        {stats['enriched']}")
    print(f"   Failed:          {stats['failed']}")
    print("=" * 70)
    
    return stats


def get_callable_leads(limit=10):
    """
    Get leads that are ready to call (have valid phones).
    Use this before cloud_multi_touch to ensure quality.
    """
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Get leads
    result = client.table("leads").select("*").in_(
        "status", ["new", "processing_email"]
    ).limit(limit * 2).execute()  # Get extra to filter
    
    callable_leads = []
    
    for lead in result.data:
        phone = lead.get("phone", "")
        agent_research = lead.get("agent_research", {})
        if isinstance(agent_research, str):
            try:
                agent_research = json.loads(agent_research)
            except:
                agent_research = {}
        
        research_phone = agent_research.get("phone", "") if agent_research else ""
        enriched_phone = agent_research.get("enriched_phone", "") if agent_research else ""
        
        # Prioritize enriched > phone field > research
        actual_phone = enriched_phone or phone or research_phone
        
        is_valid, cleaned, issue = validate_phone(actual_phone)
        
        if is_valid:
            lead["validated_phone"] = f"+1{cleaned}"
            callable_leads.append(lead)
            
            if len(callable_leads) >= limit:
                break
    
    return callable_leads


if __name__ == "__main__":
    # Run the self-healing validation
    stats = validate_and_repair_leads(limit=20)
    
    print("\n\n🎯 CALLABLE LEADS (ready for outreach):")
    callable = get_callable_leads(limit=5)
    for lead in callable:
        print(f"   {lead['company_name'][:35]:35} | {lead['validated_phone']}")
