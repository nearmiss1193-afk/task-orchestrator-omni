"""
A/B Test Tracker
Manages message variants and tracks conversion per variant.
"""
import os
import requests
import random
from datetime import datetime
from collections import defaultdict

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")


def sb_request(method, endpoint, data=None, params=None):
    """Supabase REST helper"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
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
        print(f"[AB TEST ERROR] {e}")
        return None


class ABTestTracker:
    """
    Tracks A/B test variants for email/SMS messages.
    
    Variants are stored in agent_learnings with:
    - insight_type: "ab_variant_sent"
    - metadata: {variant_id, lead_id, channel}
    
    Outcomes tracked:
    - insight_type: "ab_outcome"
    - metadata: {variant_id, outcome: opened/replied/booked}
    """
    
    # Default message variants
    EMAIL_VARIANTS = {
        "v1_sarah_intro": {
            "subject": "Quick question about {company}",
            "body": "Hi {name},\n\nI noticed {company} might be missing calls..."
        },
        "v2_direct_value": {
            "subject": "{company} - Never Miss Another Call",
            "body": "Hi {name},\n\nWhat if you never lost another lead to voicemail?"
        },
        "v3_social_proof": {
            "subject": "How {similar_company} increased bookings 40%",
            "body": "Hi {name},\n\nLocal businesses like yours are using AI..."
        }
    }
    
    SMS_VARIANTS = {
        "sms_v1_short": "Hi {name}, saw you might need help with missed calls. Quick chat? -Sarah",
        "sms_v2_question": "Hey {name}! How many calls did {company} miss last week? I can help fix that.",
        "sms_v3_offer": "{name}, free AI receptionist trial for {company}. Interested? Reply YES"
    }
    
    def __init__(self):
        pass
    
    def select_variant(self, channel: str, lead_id: str = None) -> tuple:
        """
        Randomly select a variant and record the assignment.
        Returns: (variant_id, content)
        """
        if channel == "email":
            variants = self.EMAIL_VARIANTS
        elif channel == "sms":
            variants = self.SMS_VARIANTS
        else:
            return None, None
        
        variant_id = random.choice(list(variants.keys()))
        content = variants[variant_id]
        
        # Record assignment
        if lead_id:
            sb_request("POST", "agent_learnings", data={
                "insight_type": "ab_variant_sent",
                "description": f"Assigned {variant_id} to lead",
                "metadata": {
                    "variant_id": variant_id,
                    "lead_id": lead_id,
                    "channel": channel
                },
                "created_at": datetime.utcnow().isoformat()
            })
        
        return variant_id, content
    
    def record_outcome(self, variant_id: str, outcome: str, lead_id: str = None):
        """
        Record outcome for a variant.
        Outcomes: opened, replied, booked, unsubscribed
        """
        sb_request("POST", "agent_learnings", data={
            "insight_type": "ab_outcome",
            "description": f"Variant {variant_id}: {outcome}",
            "metadata": {
                "variant_id": variant_id,
                "outcome": outcome,
                "lead_id": lead_id
            },
            "created_at": datetime.utcnow().isoformat()
        })
    
    def get_variant_stats(self) -> dict:
        """Calculate conversion rate per variant"""
        # Get all variant assignments
        sent = sb_request("GET", "agent_learnings", params={
            "insight_type": "eq.ab_variant_sent",
            "select": "metadata"
        }) or []
        
        # Get all outcomes
        outcomes = sb_request("GET", "agent_learnings", params={
            "insight_type": "eq.ab_outcome",
            "select": "metadata"
        }) or []
        
        # Count sends per variant
        send_counts = defaultdict(int)
        for s in sent:
            vid = s.get("metadata", {}).get("variant_id")
            if vid:
                send_counts[vid] += 1
        
        # Count outcomes per variant
        outcome_counts = defaultdict(lambda: defaultdict(int))
        for o in outcomes:
            meta = o.get("metadata", {})
            vid = meta.get("variant_id")
            outcome = meta.get("outcome")
            if vid and outcome:
                outcome_counts[vid][outcome] += 1
        
        # Calculate rates
        stats = {}
        for variant_id in set(list(send_counts.keys()) + list(outcome_counts.keys())):
            sent_count = send_counts.get(variant_id, 0)
            replies = outcome_counts.get(variant_id, {}).get("replied", 0)
            bookings = outcome_counts.get(variant_id, {}).get("booked", 0)
            
            stats[variant_id] = {
                "sent": sent_count,
                "replies": replies,
                "bookings": bookings,
                "reply_rate": round((replies / sent_count) * 100, 1) if sent_count > 0 else 0,
                "booking_rate": round((bookings / sent_count) * 100, 1) if sent_count > 0 else 0
            }
        
        return stats
    
    def get_best_variant(self, channel: str = "email", metric: str = "reply_rate") -> str:
        """Get the best performing variant by metric"""
        stats = self.get_variant_stats()
        
        # Filter by channel prefix
        prefix = "v" if channel == "email" else "sms_v"
        filtered = {k: v for k, v in stats.items() if k.startswith(prefix)}
        
        if not filtered:
            return list(self.EMAIL_VARIANTS.keys())[0] if channel == "email" else list(self.SMS_VARIANTS.keys())[0]
        
        # Sort by metric
        sorted_variants = sorted(filtered.items(), key=lambda x: x[1].get(metric, 0), reverse=True)
        return sorted_variants[0][0]
    
    def generate_report(self) -> str:
        """Generate A/B test performance report"""
        stats = self.get_variant_stats()
        
        report = f"""
🧪 A/B TEST PERFORMANCE REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        for variant_id, data in sorted(stats.items()):
            winner = " 🏆" if data.get("reply_rate", 0) >= 20 else ""
            report += f"""
📧 {variant_id.upper()}{winner}
   Sent:     {data['sent']}
   Replies:  {data['replies']} ({data['reply_rate']}%)
   Bookings: {data['bookings']} ({data['booking_rate']}%)
"""
        
        if not stats:
            report += "No A/B test data yet. Run outreach to collect data."
        
        return report


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    tracker = ABTestTracker()
    print(tracker.generate_report())
