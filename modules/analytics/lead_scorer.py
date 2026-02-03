"""
Lead Scoring Engine
Assigns 0-100 score based on engagement signals.
"""
import os
import requests
from datetime import datetime

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

def sb_request(method, endpoint, data=None, params=None):
    """Supabase REST helper"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=15)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=data, timeout=15)
        elif method == "PATCH":
            r = requests.patch(url, headers=headers, json=data, timeout=15)
        return r.json() if r.ok else None
    except Exception as e:
        print(f"[SUPABASE ERROR] {e}")
        return None


class LeadScorer:
    """
    Scores leads based on multiple engagement factors.
    
    Factors:
    - Email opened: +10
    - Email replied: +25
    - SMS replied: +25
    - Call answered: +30
    - Call booked meeting: +50
    - Website visited: +15
    - Form submitted: +40
    
    Decay: -5 points per week of inactivity
    """
    
    WEIGHTS = {
        "email_opened": 10,
        "email_replied": 25,
        "sms_replied": 25,
        "call_answered": 30,
        "call_booked": 50,
        "website_visit": 15,
        "form_submit": 40
    }
    
    def __init__(self):
        pass
    
    def score_lead(self, lead_id: str) -> dict:
        """Calculate score for a single lead"""
        # Get lead data
        lead = sb_request("GET", "leads", params={"id": f"eq.{lead_id}", "select": "*"})
        if not lead or len(lead) == 0:
            return {"lead_id": lead_id, "score": 0, "error": "not_found"}
        
        lead = lead[0]
        score = 0
        factors = []
        
        # Get engagement events from agent_learnings or a separate events table
        events = sb_request("GET", "agent_learnings", params={
            "select": "*",
            "metadata->>lead_id": f"eq.{lead_id}"
        }) or []
        
        # Calculate base score from events
        for event in events:
            event_type = event.get("insight_type", "")
            if event_type in self.WEIGHTS:
                score += self.WEIGHTS[event_type]
                factors.append(event_type)
        
        # Apply status bonuses
        status = lead.get("status", "new")
        if status == "contacted":
            score += 5
        elif status == "replied":
            score += 20
        elif status == "booked":
            score += 40
        elif status == "won":
            score = 100
        
        # Cap at 100
        score = min(score, 100)
        
        return {
            "lead_id": lead_id,
            "company": lead.get("company_name"),
            "score": score,
            "factors": factors,
            "status": status
        }
    
    def score_all_leads(self, limit=100) -> list:
        """Score all leads and return sorted by score"""
        leads = sb_request("GET", "leads", params={"select": "id,company_name,status", "limit": str(limit)})
        if not leads:
            return []
        
        scored = []
        for lead in leads:
            result = self.score_lead(lead["id"])
            scored.append(result)
        
        # Sort by score descending
        scored.sort(key=lambda x: x.get("score", 0), reverse=True)
        return scored
    
    def update_lead_score(self, lead_id: str, score: int):
        """Persist score to database"""
        sb_request("PATCH", f"leads?id=eq.{lead_id}", data={"lead_score": score})


def get_hot_leads(min_score=50, limit=20):
    """Get leads with score >= min_score"""
    scorer = LeadScorer()
    all_scored = scorer.score_all_leads(limit=200)
    return [l for l in all_scored if l.get("score", 0) >= min_score][:limit]


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    scorer = LeadScorer()
    print("🔥 TOP SCORED LEADS:")
    for lead in scorer.score_all_leads(limit=10):
        print(f"  {lead['score']:3d} | {lead.get('company', 'Unknown'):30s} | {lead.get('status', 'new')}")
