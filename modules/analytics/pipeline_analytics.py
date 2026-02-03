"""
Pipeline Analytics
Generates conversion funnel metrics and reports.
"""
import os
import requests
from datetime import datetime, timedelta
from collections import Counter

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def sb_request(method, endpoint, params=None):
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
        r = requests.get(url, headers=headers, timeout=15)
        return r.json() if r.ok else []
    except:
        return []


class PipelineAnalytics:
    """
    Tracks conversion through the sales funnel:
    
    Funnel Stages:
    1. Prospected (new)
    2. Contacted (email/sms sent)
    3. Engaged (replied)
    4. Qualified (call completed)
    5. Booked (meeting scheduled)
    6. Won (closed deal)
    """
    
    STAGES = ["new", "contacted", "engaged", "qualified", "booked", "won"]
    
    def get_funnel_metrics(self) -> dict:
        """Calculate conversion rates at each stage"""
        leads = sb_request("GET", "leads", params={"select": "status"})
        
        if not leads:
            return {"error": "no_data"}
        
        # Count by status
        status_counts = Counter(l.get("status", "new") for l in leads)
        
        # Map to funnel stages
        funnel = {}
        total = len(leads)
        
        for stage in self.STAGES:
            count = status_counts.get(stage, 0)
            funnel[stage] = {
                "count": count,
                "percentage": round((count / total) * 100, 1) if total > 0 else 0
            }
        
        # Calculate stage-to-stage conversion
        conversions = {}
        for i, stage in enumerate(self.STAGES[:-1]):
            next_stage = self.STAGES[i + 1]
            current = funnel[stage]["count"]
            next_count = funnel[next_stage]["count"]
            
            if current > 0:
                rate = round((next_count / current) * 100, 1)
            else:
                rate = 0
            
            conversions[f"{stage}_to_{next_stage}"] = rate
        
        return {
            "total_leads": total,
            "funnel": funnel,
            "conversions": conversions
        }
    
    def get_daily_activity(self, days=7) -> list:
        """Get activity counts per day"""
        results = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            
            # Count leads created on this date
            leads = sb_request("GET", "leads", params={
                "select": "id",
                "created_at": f"gte.{date}T00:00:00",
                "created_at": f"lt.{date}T23:59:59"
            })
            
            results.append({
                "date": date,
                "new_leads": len(leads) if leads else 0
            })
        
        return list(reversed(results))
    
    def get_response_rates(self) -> dict:
        """Calculate email and SMS response rates"""
        # Get outreach events
        events = sb_request("GET", "agent_learnings", params={"select": "insight_type"})
        
        if not events:
            return {"email_rate": 0, "sms_rate": 0, "call_rate": 0}
        
        types = Counter(e.get("insight_type", "") for e in events)
        
        # Calculate rates
        email_sent = types.get("email_sent", 0)
        email_reply = types.get("email_replied", 0)
        
        sms_sent = types.get("sms_sent", 0)
        sms_reply = types.get("sms_replied", 0)
        
        calls_made = types.get("call_made", 0)
        calls_answered = types.get("call_answered", 0)
        
        return {
            "email_response_rate": round((email_reply / email_sent) * 100, 1) if email_sent > 0 else 0,
            "sms_response_rate": round((sms_reply / sms_sent) * 100, 1) if sms_sent > 0 else 0,
            "call_answer_rate": round((calls_answered / calls_made) * 100, 1) if calls_made > 0 else 0,
            "raw_counts": {
                "emails_sent": email_sent,
                "emails_replied": email_reply,
                "sms_sent": sms_sent,
                "sms_replied": sms_reply,
                "calls_made": calls_made,
                "calls_answered": calls_answered
            }
        }
    
    def generate_report(self) -> str:
        """Generate human-readable analytics report"""
        funnel = self.get_funnel_metrics()
        rates = self.get_response_rates()
        
        report = f"""
📊 PIPELINE ANALYTICS REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 FUNNEL OVERVIEW
Total Leads: {funnel.get('total_leads', 0)}

Stage Breakdown:
"""
        
        for stage, data in funnel.get("funnel", {}).items():
            bar = "█" * (data["count"] // 10) if data["count"] > 0 else "░"
            report += f"  {stage.upper():12s} | {data['count']:4d} ({data['percentage']:5.1f}%) {bar}\n"
        
        report += f"""
📧 RESPONSE RATES
  Email: {rates.get('email_response_rate', 0):.1f}%
  SMS:   {rates.get('sms_response_rate', 0):.1f}%
  Calls: {rates.get('call_answer_rate', 0):.1f}%

📊 RAW ACTIVITY
"""
        for key, val in rates.get("raw_counts", {}).items():
            report += f"  {key}: {val}\n"
        
        return report


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    analytics = PipelineAnalytics()
    print(analytics.generate_report())
