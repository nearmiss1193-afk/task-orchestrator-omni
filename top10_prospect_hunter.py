"""
TOP 10 PROSPECT HUNTER
======================
Identifies the 10 highest-probability conversion prospects using Deep Intel Agent.
Generates detailed reports with cost-savings analysis and personalized outreach messages.

Usage:
    python top10_prospect_hunter.py
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Import our agents
from deep_intel_agent import DeepIntelAgent
from modules.grok_client import GrokClient

# Florida HVAC target companies - high value prospects
TOP_FLORIDA_HVAC_TARGETS = [
    {"company": "Homeheart HVAC & Cool", "city": "Lakeland", "state": "FL"},
    {"company": "Cool Breeze Air Conditioning", "city": "Tampa", "state": "FL"},
    {"company": "Florida Air Systems", "city": "Tampa", "state": "FL"},
    {"company": "Bay Area Comfort Solutions", "city": "Clearwater", "state": "FL"},
    {"company": "Magic City Cooling", "city": "Orlando", "state": "FL"},
    {"company": "Central Florida HVAC Pros", "city": "Orlando", "state": "FL"},
    {"company": "Sunshine State Air", "city": "Jacksonville", "state": "FL"},
    {"company": "Gulf Coast Climate Control", "city": "Sarasota", "state": "FL"},
    {"company": "Paradise AC Services", "city": "Fort Myers", "state": "FL"},
    {"company": "Polk County Heating & Air", "city": "Lakeland", "state": "FL"},
    {"company": "Tampa Bay AC Specialists", "city": "St. Petersburg", "state": "FL"},
    {"company": "Orlando Comfort Masters", "city": "Orlando", "state": "FL"},
]


def calculate_savings_potential(dossier: Dict) -> Dict[str, Any]:
    """Calculate potential cost savings for a prospect"""
    grok = GrokClient()
    
    reviews = dossier.get("reviews", {})
    google_reviews = reviews.get("google", {}).get("count", 50)
    
    # Estimate missed calls based on review volume (proxy for call volume)
    estimated_monthly_calls = google_reviews * 3  # Rough estimate
    estimated_missed_calls = int(estimated_monthly_calls * 0.25)  # 25% miss rate
    avg_job_value = 450  # HVAC average
    
    monthly_lost_revenue = estimated_missed_calls * avg_job_value * 0.3  # 30% would convert
    annual_lost_revenue = monthly_lost_revenue * 12
    
    our_monthly_cost = 199  # HVAC Lite plan
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
    """Generate personalized outreach message using Grok"""
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


def run_top10_hunt():
    """Run the full top 10 prospect hunt with intel and messages"""
    print("=" * 70)
    print("🎯 TOP 10 PROSPECT HUNTER")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)
    
    agent = DeepIntelAgent()
    all_prospects = []
    
    # Gather intel on all targets
    print(f"\n📡 Deploying Deep Intel Agent on {len(TOP_FLORIDA_HVAC_TARGETS)} targets...")
    
    for i, target in enumerate(TOP_FLORIDA_HVAC_TARGETS[:12], 1):
        print(f"\n[{i}/12] {target['company']} ({target['city']}, {target['state']})")
        
        try:
            dossier = agent.gather_intel(
                target["company"],
                target["city"],
                target["state"]
            )
            
            # Calculate savings potential
            savings = calculate_savings_potential(dossier)
            dossier["savings_analysis"] = savings
            
            # Score for prioritization
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
    
    # Sort by priority score
    all_prospects.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
    
    # Take top 10
    top10 = all_prospects[:10]
    
    print("\n" + "=" * 70)
    print("🏆 TOP 10 HIGHEST-PROBABILITY PROSPECTS")
    print("=" * 70)
    
    # Generate personalized messages for top 10
    for i, prospect in enumerate(top10, 1):
        print(f"\n{'─' * 60}")
        print(f"#{i}: {prospect['company_name']} ({prospect['city']}, {prospect['state']})")
        print(f"    Priority Score: {prospect.get('priority_score', 0)}")
        
        # Contact info
        contacts = prospect.get("contacts", [])
        if contacts:
            print(f"    👤 Contact: {contacts[0].get('name', 'N/A')} - {contacts[0].get('title', 'N/A')}")
            print(f"    📧 Email: {contacts[0].get('email', 'N/A')}")
        
        # Savings
        savings = prospect.get("savings_analysis", {})
        print(f"    💰 Est. Monthly Lost Revenue: ${savings.get('monthly_lost_revenue', 0):,.0f}")
        print(f"    💵 Est. Annual Savings with AI: ${savings.get('net_annual_savings', 0):,.0f}")
        print(f"    📈 ROI: {savings.get('roi_multiplier', 0)}x")
        
        # Generate message
        print(f"    📝 Generating personalized message...")
        message = generate_personalized_message(prospect, savings)
        prospect["personalized_message"] = message
        print(f"    ✉️ Subject: {message.get('subject', 'N/A')}")
    
    # Save results
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_analyzed": len(all_prospects),
        "top_10_prospects": top10
    }
    
    os.makedirs("campaign_data", exist_ok=True)
    output_file = f"campaign_data/top10_prospects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"📁 Full report saved: {output_file}")
    print("=" * 70)
    
    return output


if __name__ == "__main__":
    run_top10_hunt()
