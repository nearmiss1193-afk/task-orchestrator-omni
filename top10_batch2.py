"""
TOP 10 PROSPECT HUNTER - BATCH 2
================================
Second wave of Florida HVAC prospects.
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from deep_intel_agent import DeepIntelAgent
from modules.grok_client import GrokClient

# BATCH 2 - New Florida cities and companies
BATCH_2_TARGETS = [
    {"company": "Gainesville Air Comfort", "city": "Gainesville", "state": "FL"},
    {"company": "Pensacola Climate Solutions", "city": "Pensacola", "state": "FL"},
    {"company": "Tallahassee AC Experts", "city": "Tallahassee", "state": "FL"},
    {"company": "Daytona Beach HVAC Services", "city": "Daytona Beach", "state": "FL"},
    {"company": "Palm Beach Air Systems", "city": "West Palm Beach", "state": "FL"},
    {"company": "Boca Raton Cooling Co", "city": "Boca Raton", "state": "FL"},
    {"company": "Naples Comfort Air", "city": "Naples", "state": "FL"},
    {"company": "Ocala Air Conditioning", "city": "Ocala", "state": "FL"},
    {"company": "Port St. Lucie HVAC", "city": "Port St. Lucie", "state": "FL"},
    {"company": "Cape Coral Climate Control", "city": "Cape Coral", "state": "FL"},
    {"company": "Melbourne AC Pros", "city": "Melbourne", "state": "FL"},
    {"company": "Bradenton Heating & Air", "city": "Bradenton", "state": "FL"},
]


def calculate_savings_potential(dossier: Dict) -> Dict[str, Any]:
    reviews = dossier.get("reviews", {})
    google_reviews = reviews.get("google", {}).get("count", 50)
    estimated_monthly_calls = google_reviews * 3
    estimated_missed_calls = int(estimated_monthly_calls * 0.25)
    avg_job_value = 450
    monthly_lost_revenue = estimated_missed_calls * avg_job_value * 0.3
    annual_lost_revenue = monthly_lost_revenue * 12
    our_monthly_cost = 199
    our_annual_cost = our_monthly_cost * 12
    net_annual_savings = annual_lost_revenue - our_annual_cost
    roi_multiplier = annual_lost_revenue / our_annual_cost if our_annual_cost > 0 else 0
    
    return {
        "estimated_monthly_calls": estimated_monthly_calls,
        "estimated_missed_calls_monthly": estimated_missed_calls,
        "avg_job_value": avg_job_value,
        "monthly_lost_revenue": round(monthly_lost_revenue, 2),
        "annual_lost_revenue": round(annual_lost_revenue, 2),
        "our_monthly_cost": our_monthly_cost,
        "our_annual_cost": our_annual_cost,
        "net_annual_savings": round(net_annual_savings, 2),
        "roi_multiplier": round(roi_multiplier, 1),
        "payback_period_days": round(30 / roi_multiplier, 0) if roi_multiplier > 0 else 999
    }


def generate_personalized_message(dossier: Dict, savings: Dict) -> Dict[str, str]:
    grok = GrokClient()
    company = dossier["company_name"]
    city = dossier["city"]
    contact = dossier.get("contacts", [{}])[0]
    contact_name = contact.get("name", "there")
    monthly_loss = savings.get("monthly_lost_revenue", 5000)
    
    prompt = f"""Write a personalized cold email for:
Company: {company}
City: {city}, FL
Contact: {contact_name}
Their monthly missed call revenue loss: ${monthly_loss:,.0f}

The email should:
- Open with a specific observation about their business
- Mention the estimated revenue they're losing
- Offer our AI phone agent solution
- Be under 100 words
- End with a soft question

Return JSON: {{"subject": "...", "body": "..."}}
Only return the JSON."""

    try:
        response = grok.ask(prompt)
        if "{" in response:
            json_str = response[response.index("{"):response.rindex("}")+1]
            return json.loads(json_str)
    except Exception as e:
        print(f"    ⚠️ Message generation failed: {e}")
    
    return {
        "subject": f"Quick question about {company}",
        "body": f"Hey {contact_name},\n\nI noticed {company} is doing great work in {city}. Quick question - how are you handling after-hours calls right now?\n\nBased on your online presence, I estimate you might be missing ${monthly_loss:,.0f}/month in potential revenue from unanswered calls.\n\nWould it be worth a 10-minute chat to see if our AI phone agent could help?\n\nBest,\nDaniel\nAI Service Co"
    }


def run_batch_2():
    print("=" * 70)
    print("🎯 TOP 10 PROSPECT HUNTER - BATCH 2")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)
    
    agent = DeepIntelAgent()
    all_prospects = []
    
    print(f"\n📡 Deploying Deep Intel Agent on {len(BATCH_2_TARGETS)} NEW targets...")
    
    for i, target in enumerate(BATCH_2_TARGETS, 1):
        print(f"\n[{i}/12] {target['company']} ({target['city']}, {target['state']})")
        
        try:
            dossier = agent.gather_intel(target["company"], target["city"], target["state"])
            savings = calculate_savings_potential(dossier)
            dossier["savings_analysis"] = savings
            
            score = (
                savings["roi_multiplier"] * 10 +
                dossier.get("reviews", {}).get("google", {}).get("rating", 3) * 5 +
                (100 if dossier.get("contacts") else 0)
            )
            dossier["priority_score"] = round(score, 1)
            all_prospects.append(dossier)
            print(f"    ✅ Score: {score:.1f} | Est. Annual Savings: ${savings['net_annual_savings']:,.0f}")
        except Exception as e:
            print(f"    ❌ Failed: {e}")
    
    all_prospects.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
    top10 = all_prospects[:10]
    
    print("\n" + "=" * 70)
    print("🏆 BATCH 2 - TOP 10 PROSPECTS")
    print("=" * 70)
    
    for i, prospect in enumerate(top10, 1):
        print(f"\n{'─' * 60}")
        print(f"#{i}: {prospect['company_name']} ({prospect['city']}, {prospect['state']})")
        print(f"    Priority Score: {prospect.get('priority_score', 0)}")
        
        contacts = prospect.get("contacts", [])
        if contacts:
            print(f"    👤 Contact: {contacts[0].get('name', 'N/A')} - {contacts[0].get('title', 'N/A')}")
            print(f"    📧 Email: {contacts[0].get('email', 'N/A')}")
        
        savings = prospect.get("savings_analysis", {})
        print(f"    💰 Est. Monthly Lost Revenue: ${savings.get('monthly_lost_revenue', 0):,.0f}")
        print(f"    📈 ROI: {savings.get('roi_multiplier', 0)}x")
        
        print(f"    📝 Generating personalized message...")
        message = generate_personalized_message(prospect, savings)
        prospect["personalized_message"] = message
        print(f"    ✉️ Subject: {message.get('subject', 'N/A')}")
    
    output = {
        "batch": 2,
        "generated_at": datetime.now().isoformat(),
        "total_analyzed": len(all_prospects),
        "top_10_prospects": top10
    }
    
    os.makedirs("campaign_data", exist_ok=True)
    output_file = f"campaign_data/top10_batch2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"📁 Batch 2 report saved: {output_file}")
    print("=" * 70)
    
    return output


if __name__ == "__main__":
    run_batch_2()
