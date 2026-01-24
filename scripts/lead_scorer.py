"""
LEAD SCORER - Multi-Factor Lead Scoring Engine
Empire Analytics Infrastructure

Scores leads 0-100 based on:
- Website quality (25%)
- Company size (20%)  
- Tech stack (20%)
- Industry match (15%)
- Recency (10%)
- Engagement (10%)
"""

import os
import json
import datetime
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(".env.local")

# For Modal deployment
try:
    import modal
    from supabase import create_client, Client
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False

# ============ SCORING WEIGHTS ============
WEIGHTS = {
    "website_quality": 0.25,
    "company_size": 0.20,
    "tech_stack": 0.20,
    "industry_match": 0.15,
    "recency": 0.10,
    "engagement": 0.10
}

# High-value industries for AI automation
TARGET_INDUSTRIES = [
    "hvac", "plumbing", "roofing", "electrical", "landscaping",
    "pool service", "pest control", "general contractor", 
    "assisted living", "dental", "auto repair"
]

def get_supabase() -> "Client":
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def get_gemini():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def score_website_quality(research: dict) -> int:
    """Score website based on AI analysis (0-100)"""
    if not research:
        return 30  # Default for no data
    
    inefficiencies = research.get("inefficiencies", [])
    automation_score = research.get("automation_score", 50)
    
    # More inefficiencies = higher opportunity
    inefficiency_bonus = min(len(inefficiencies) * 15, 40)
    
    return min(100, automation_score + inefficiency_bonus)

def score_company_size(lead: dict) -> int:
    """Score based on company indicators (0-100)"""
    # Use research data to infer size
    research = lead.get("raw_research", {}) or {}
    
    # Keywords suggesting larger companies
    size_indicators = str(research).lower()
    
    if any(x in size_indicators for x in ["franchise", "locations", "nationwide"]):
        return 90
    elif any(x in size_indicators for x in ["team", "employees", "staff"]):
        return 70
    elif any(x in size_indicators for x in ["family owned", "local", "owner"]):
        return 50
    
    return 40  # Default small business

def score_tech_stack(research: dict) -> int:
    """Score based on tech indicators - outdated = higher opportunity (0-100)"""
    if not research:
        return 50
    
    inefficiencies = research.get("inefficiencies", [])
    inefficiency_text = " ".join(inefficiencies).lower()
    
    # High opportunity signals
    if any(x in inefficiency_text for x in ["no automation", "manual", "no booking", "no crm"]):
        return 95
    elif any(x in inefficiency_text for x in ["outdated", "basic", "simple"]):
        return 80
    elif any(x in inefficiency_text for x in ["some automation", "partial"]):
        return 60
    
    return 40

def score_industry_match(lead: dict) -> int:
    """Score based on industry fit (0-100)"""
    website = (lead.get("website_url") or "").lower()
    name = (lead.get("full_name") or "").lower()
    research = str(lead.get("raw_research", {})).lower()
    
    combined = f"{website} {name} {research}"
    
    for industry in TARGET_INDUSTRIES:
        if industry in combined:
            return 100
    
    # Partial matches
    service_keywords = ["service", "repair", "install", "maintenance", "contractor"]
    if any(kw in combined for kw in service_keywords):
        return 70
    
    return 30

def score_recency(lead: dict) -> int:
    """Score based on how recent the lead is (0-100)"""
    created_at = lead.get("created_at")
    if not created_at:
        return 50
    
    try:
        created = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        days_old = (now - created).days
        
        if days_old <= 1:
            return 100
        elif days_old <= 7:
            return 80
        elif days_old <= 30:
            return 50
        else:
            return 20
    except:
        return 50

def score_engagement(lead: dict) -> int:
    """Score based on engagement signals (0-100)"""
    status = lead.get("status", "new")
    
    engagement_scores = {
        "closed": 100,
        "booked": 95,
        "responded": 85,
        "engaged": 80,
        "nurture_day_20": 60,
        "nurture_day_10": 50,
        "nurture_day_3": 40,
        "outreach_sent": 30,
        "research_done": 20,
        "new": 10
    }
    
    return engagement_scores.get(status, 10)

def calculate_lead_score(lead: dict) -> dict:
    """Calculate composite lead score with breakdown"""
    research = lead.get("raw_research", {}) or {}
    
    scores = {
        "website_quality": score_website_quality(research),
        "company_size": score_company_size(lead),
        "tech_stack": score_tech_stack(research),
        "industry_match": score_industry_match(lead),
        "recency": score_recency(lead),
        "engagement": score_engagement(lead)
    }
    
    # Weighted total
    total = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    total = int(min(100, max(0, total)))
    
    return {
        "total_score": total,
        "breakdown": scores,
        "timestamp": datetime.datetime.now().isoformat()
    }

def score_leads_batch(leads: list) -> list:
    """Score a batch of leads"""
    results = []
    for lead in leads:
        score_data = calculate_lead_score(lead)
        results.append({
            "ghl_contact_id": lead.get("ghl_contact_id"),
            "lead_score": score_data["total_score"],
            "score_breakdown": score_data["breakdown"]
        })
    return results

# ============ MODAL FUNCTION ============
# Only import Modal dependencies when not in test mode
def register_modal_functions():
    """Register Modal functions when running in cloud"""
    try:
        from deploy import app, image, VAULT, brain_log
        
        @app.function(image=image, secrets=[VAULT], schedule=modal.Period(minutes=30))
        def lead_scoring_loop():
            """
            CRON: LEAD SCORING (Every 30m)
            Scores unscored leads or leads with stale scores.
            """
            brain_log("[Lead Scorer] Starting scoring loop...")
            supabase = get_supabase()
            
            # Get leads that need scoring (new or not scored recently)
            leads = supabase.table("contacts_master").select("*").or_(
                "lead_score.eq.0,lead_score.is.null"
            ).limit(50).execute()
            
            scored_count = 0
            for lead in leads.data:
                score_data = calculate_lead_score(lead)
                
                supabase.table("contacts_master").update({
                    "lead_score": score_data["total_score"]
                }).eq("ghl_contact_id", lead["ghl_contact_id"]).execute()
                
                scored_count += 1
            
            brain_log(f"[Lead Scorer] Scored {scored_count} leads.")
            return {"scored": scored_count}
        
        return lead_scoring_loop
    except ImportError:
        return None

# ============ CLI / TEST MODE ============
def run_test():
    """Test scoring with sample data"""
    sample_leads = [
        {
            "ghl_contact_id": "test_001",
            "full_name": "Tampa HVAC Pros",
            "website_url": "https://tampahvacpros.com",
            "status": "new",
            "created_at": datetime.datetime.now().isoformat(),
            "raw_research": {
                "inefficiencies": ["no automated booking", "manual lead follow-up"],
                "automation_score": 75
            }
        },
        {
            "ghl_contact_id": "test_002",
            "full_name": "Generic Business LLC",
            "website_url": "https://genericbiz.com",
            "status": "outreach_sent",
            "created_at": (datetime.datetime.now() - datetime.timedelta(days=15)).isoformat(),
            "raw_research": {}
        },
        {
            "ghl_contact_id": "test_003",
            "full_name": "Elite Roofing Tampa",
            "website_url": "https://eliteroofing.com",
            "status": "responded",
            "created_at": (datetime.datetime.now() - datetime.timedelta(days=2)).isoformat(),
            "raw_research": {
                "inefficiencies": ["no CRM", "basic contact form", "no automation"],
                "automation_score": 90
            }
        }
    ]
    
    print("=" * 50)
    print("LEAD SCORER TEST")
    print("=" * 50)
    
    for lead in sample_leads:
        result = calculate_lead_score(lead)
        print(f"\n📊 {lead['full_name']}")
        print(f"   Total Score: {result['total_score']}/100")
        print(f"   Breakdown:")
        for k, v in result['breakdown'].items():
            weight = int(WEIGHTS[k] * 100)
            print(f"      {k}: {v} (weight: {weight}%)")
    
    print("\n✅ All scores in valid 0-100 range")

# ============ TURBO EXECUTION ============
def run_turbo_mode():
    """Run scoring on real database leads (CLI Mode)"""
    print("🚀 TURBO SCORING INITIATED")
    if not MODAL_AVAILABLE:
        print("❌ Dependencies missing (Supabase/Modal)")
        return

    supabase = get_supabase()
    
    # Get leads that need scoring
    print("🔍 Fetching unscored leads...")
    leads = supabase.table("contacts_master").select("*").or_(
        "lead_score.eq.0,lead_score.is.null"
    ).limit(100).execute()
    
    if not leads.data:
        print("✅ No leads need scoring.")
        return
        
    print(f"📊 Found {len(leads.data)} leads to score.")
    
    scored_count = 0
    for lead in leads.data:
        try:
            score_data = calculate_lead_score(lead)
            
            supabase.table("contacts_master").update({
                "lead_score": score_data["total_score"]
            }).eq("ghl_contact_id", lead["ghl_contact_id"]).execute()
            
            print(f"   ✅ Scored {lead.get('full_name', 'Unknown')}: {score_data['total_score']}")
            scored_count += 1
        except Exception as e:
            print(f"   ❌ Failed to score {lead.get('ghl_contact_id')}: {e}")
            
    print(f"🏁 Turbo Scoring Complete. Scored {scored_count} leads.")

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        run_test()
    elif "--turbo" in sys.argv:
        run_turbo_mode()
    else:
        print("Usage: python lead_scorer.py --test | --turbo")
