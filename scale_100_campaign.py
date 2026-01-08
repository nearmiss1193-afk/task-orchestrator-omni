"""
SCALED HVAC CAMPAIGN - 100 PROSPECTS
=====================================
Gathers deep intel on 100 Florida HVAC companies and sends rate-limited outreach.

Features:
- Deep Intel on 100 prospects across 25 Florida cities
- Rate limiting: 20 emails per 10 minutes (avoid spam)
- Personalized Grok messages
- Video link integration
- Call sheet generation
- Campaign logging

Usage:
    python scale_100_campaign.py --intel    # Just gather intel
    python scale_100_campaign.py --send     # Send emails (rate limited)
    python scale_100_campaign.py --all      # Both
"""
import os
import json
import time
import argparse
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Import our agents
from deep_intel_agent import DeepIntelAgent
from modules.grok_client import GrokClient
import resend

resend.api_key = os.getenv('RESEND_API_KEY')

# Configuration
VIDEO_URL = "https://youtube.com/shorts/C4GRQ8xaFn0"
CALENDLY_LINK = "https://calendly.com/aiserviceco/demo"
RATE_LIMIT = 20  # emails per batch
RATE_WINDOW = 600  # 10 minutes in seconds

# 100 Florida HVAC targets across 25 cities (4 per city)
FLORIDA_HVAC_TARGETS = [
    # Tampa Bay Area
    {"company": "Tampa Bay Cooling Services", "city": "Tampa", "state": "FL"},
    {"company": "Brandon HVAC Solutions", "city": "Tampa", "state": "FL"},
    {"company": "Hillsborough Air & Heat", "city": "Tampa", "state": "FL"},
    {"company": "Wesley Chapel AC Pros", "city": "Tampa", "state": "FL"},
    
    # Orlando Metro
    {"company": "Orlando Comfort Air", "city": "Orlando", "state": "FL"},
    {"company": "Kissimmee HVAC Masters", "city": "Orlando", "state": "FL"},
    {"company": "Winter Park Cooling Co", "city": "Orlando", "state": "FL"},
    {"company": "Lake Nona AC Services", "city": "Orlando", "state": "FL"},
    
    # Miami-Dade
    {"company": "Miami Climate Control", "city": "Miami", "state": "FL"},
    {"company": "Doral AC Specialists", "city": "Miami", "state": "FL"},
    {"company": "Kendall Cooling Systems", "city": "Miami", "state": "FL"},
    {"company": "Hialeah HVAC Pros", "city": "Miami", "state": "FL"},
    
    # Fort Lauderdale / Broward
    {"company": "Fort Lauderdale Air Systems", "city": "Fort Lauderdale", "state": "FL"},
    {"company": "Pompano Beach HVAC", "city": "Fort Lauderdale", "state": "FL"},
    {"company": "Coral Springs Cooling", "city": "Fort Lauderdale", "state": "FL"},
    {"company": "Plantation AC Services", "city": "Fort Lauderdale", "state": "FL"},
    
    # Jacksonville
    {"company": "Jax Beach Air Conditioning", "city": "Jacksonville", "state": "FL"},
    {"company": "Southside HVAC Solutions", "city": "Jacksonville", "state": "FL"},
    {"company": "Orange Park Cooling", "city": "Jacksonville", "state": "FL"},
    {"company": "Mandarin AC Pros", "city": "Jacksonville", "state": "FL"},
    
    # St. Petersburg / Clearwater
    {"company": "St Pete Beach HVAC", "city": "St. Petersburg", "state": "FL"},
    {"company": "Pinellas Air Solutions", "city": "St. Petersburg", "state": "FL"},
    {"company": "Largo Cooling Services", "city": "Clearwater", "state": "FL"},
    {"company": "Dunedin AC Experts", "city": "Clearwater", "state": "FL"},
    
    # West Palm Beach
    {"company": "Palm Beach Gardens HVAC", "city": "West Palm Beach", "state": "FL"},
    {"company": "Jupiter Air Conditioning", "city": "West Palm Beach", "state": "FL"},
    {"company": "Lake Worth Cooling", "city": "West Palm Beach", "state": "FL"},
    {"company": "Wellington AC Services", "city": "West Palm Beach", "state": "FL"},
    
    # Sarasota / Bradenton
    {"company": "Sarasota Bay HVAC", "city": "Sarasota", "state": "FL"},
    {"company": "Venice Air Systems", "city": "Sarasota", "state": "FL"},
    {"company": "Bradenton Beach AC", "city": "Bradenton", "state": "FL"},
    {"company": "Palmetto Cooling Co", "city": "Bradenton", "state": "FL"},
    
    # Fort Myers / Cape Coral
    {"company": "Fort Myers Beach HVAC", "city": "Fort Myers", "state": "FL"},
    {"company": "Bonita Springs Cooling", "city": "Fort Myers", "state": "FL"},
    {"company": "Lehigh Acres AC", "city": "Fort Myers", "state": "FL"},
    {"company": "Estero Air Solutions", "city": "Fort Myers", "state": "FL"},
    
    # Lakeland / Polk County
    {"company": "Lakeland Air Comfort", "city": "Lakeland", "state": "FL"},
    {"company": "Winter Haven HVAC", "city": "Lakeland", "state": "FL"},
    {"company": "Bartow Cooling Services", "city": "Lakeland", "state": "FL"},
    {"company": "Haines City AC Pros", "city": "Lakeland", "state": "FL"},
    
    # Daytona / Volusia
    {"company": "Daytona Shores HVAC", "city": "Daytona Beach", "state": "FL"},
    {"company": "Port Orange Cooling", "city": "Daytona Beach", "state": "FL"},
    {"company": "DeLand AC Services", "city": "Daytona Beach", "state": "FL"},
    {"company": "New Smyrna HVAC", "city": "Daytona Beach", "state": "FL"},
    
    # Gainesville
    {"company": "Gator HVAC Services", "city": "Gainesville", "state": "FL"},
    {"company": "Alachua Air Systems", "city": "Gainesville", "state": "FL"},
    {"company": "Newberry Cooling Co", "city": "Gainesville", "state": "FL"},
    {"company": "High Springs AC", "city": "Gainesville", "state": "FL"},
    
    # Tallahassee
    {"company": "Capital City HVAC", "city": "Tallahassee", "state": "FL"},
    {"company": "Leon County Cooling", "city": "Tallahassee", "state": "FL"},
    {"company": "Killearn AC Services", "city": "Tallahassee", "state": "FL"},
    {"company": "Southwood Air Systems", "city": "Tallahassee", "state": "FL"},
    
    # Pensacola
    {"company": "Pensacola Beach HVAC", "city": "Pensacola", "state": "FL"},
    {"company": "Gulf Breeze Cooling", "city": "Pensacola", "state": "FL"},
    {"company": "Escambia Air Services", "city": "Pensacola", "state": "FL"},
    {"company": "Navarre AC Pros", "city": "Pensacola", "state": "FL"},
    
    # Panama City
    {"company": "Panama City Beach HVAC", "city": "Panama City", "state": "FL"},
    {"company": "Lynn Haven Cooling", "city": "Panama City", "state": "FL"},
    {"company": "Bay County AC", "city": "Panama City", "state": "FL"},
    {"company": "Callaway Air Systems", "city": "Panama City", "state": "FL"},
    
    # Ocala / Marion
    {"company": "Ocala Forest HVAC", "city": "Ocala", "state": "FL"},
    {"company": "Silver Springs Cooling", "city": "Ocala", "state": "FL"},
    {"company": "Belleview AC Services", "city": "Ocala", "state": "FL"},
    {"company": "Marion Oaks Air", "city": "Ocala", "state": "FL"},
    
    # Naples
    {"company": "Naples Beach HVAC", "city": "Naples", "state": "FL"},
    {"company": "Marco Island Cooling", "city": "Naples", "state": "FL"},
    {"company": "Collier County AC", "city": "Naples", "state": "FL"},
    {"company": "Ave Maria Air Systems", "city": "Naples", "state": "FL"},
    
    # Melbourne / Space Coast
    {"company": "Melbourne Beach HVAC", "city": "Melbourne", "state": "FL"},
    {"company": "Palm Bay Cooling", "city": "Melbourne", "state": "FL"},
    {"company": "Cocoa Beach AC", "city": "Melbourne", "state": "FL"},
    {"company": "Titusville Air Services", "city": "Melbourne", "state": "FL"},
    
    # Port St. Lucie / Treasure Coast
    {"company": "Port St Lucie Beach HVAC", "city": "Port St. Lucie", "state": "FL"},
    {"company": "Jensen Beach Cooling", "city": "Port St. Lucie", "state": "FL"},
    {"company": "Stuart AC Services", "city": "Port St. Lucie", "state": "FL"},
    {"company": "Vero Beach Air", "city": "Port St. Lucie", "state": "FL"},
    
    # Boca Raton / Delray
    {"company": "Boca Beach HVAC", "city": "Boca Raton", "state": "FL"},
    {"company": "Delray Cooling Solutions", "city": "Boca Raton", "state": "FL"},
    {"company": "Boynton Beach AC", "city": "Boca Raton", "state": "FL"},
    {"company": "Highland Beach Air", "city": "Boca Raton", "state": "FL"},
    
    # Homestead / Florida Keys
    {"company": "Homestead HVAC Services", "city": "Homestead", "state": "FL"},
    {"company": "Florida City Cooling", "city": "Homestead", "state": "FL"},
    {"company": "Key Largo AC", "city": "Homestead", "state": "FL"},
    {"company": "Islamorada Air Systems", "city": "Homestead", "state": "FL"},
    
    # Spring Hill / Hernando
    {"company": "Spring Hill HVAC", "city": "Spring Hill", "state": "FL"},
    {"company": "Brooksville Cooling", "city": "Spring Hill", "state": "FL"},
    {"company": "Hernando County AC", "city": "Spring Hill", "state": "FL"},
    {"company": "Weeki Wachee Air", "city": "Spring Hill", "state": "FL"},
    
    # Deltona / Volusia
    {"company": "Deltona HVAC Solutions", "city": "Deltona", "state": "FL"},
    {"company": "Orange City Cooling", "city": "Deltona", "state": "FL"},
    {"company": "DeBary AC Services", "city": "Deltona", "state": "FL"},
    {"company": "Sanford Air Systems", "city": "Deltona", "state": "FL"},
    
    # Palm Coast / Flagler
    {"company": "Palm Coast HVAC", "city": "Palm Coast", "state": "FL"},
    {"company": "Flagler Beach Cooling", "city": "Palm Coast", "state": "FL"},
    {"company": "Bunnell AC Services", "city": "Palm Coast", "state": "FL"},
    {"company": "Hammock Air Systems", "city": "Palm Coast", "state": "FL"},
]


def calculate_savings(dossier: Dict) -> Dict[str, Any]:
    """Calculate potential savings for prospect"""
    reviews = dossier.get("reviews", {})
    google_reviews = reviews.get("google", {}).get("count", 50)
    estimated_monthly_calls = google_reviews * 3
    estimated_missed_calls = int(estimated_monthly_calls * 0.25)
    avg_job_value = 450
    monthly_lost = estimated_missed_calls * avg_job_value * 0.3
    annual_lost = monthly_lost * 12
    our_cost = 199 * 12
    
    return {
        "monthly_lost_revenue": round(monthly_lost, 2),
        "annual_lost_revenue": round(annual_lost, 2),
        "net_annual_savings": round(annual_lost - our_cost, 2),
        "roi_multiplier": round(annual_lost / our_cost, 1) if our_cost > 0 else 0
    }


def generate_message(dossier: Dict, savings: Dict) -> Dict[str, str]:
    """Generate personalized email message"""
    grok = GrokClient()
    company = dossier["company_name"]
    city = dossier["city"]
    contact = dossier.get("contacts", [{}])[0]
    name = contact.get("name", "there")
    monthly_loss = savings.get("monthly_lost_revenue", 5000)
    
    prompt = f"""Write a short cold email for:
Company: {company}
City: {city}, FL
Contact: {name}
Monthly missed call loss: ${monthly_loss:,.0f}

Rules:
- Under 80 words
- Open with specific observation
- Mention revenue loss
- Offer AI phone agent
- Soft CTA question

Return JSON: {{"subject": "...", "body": "..."}}
Only return JSON."""

    try:
        response = grok.ask(prompt)
        if "{" in response:
            json_str = response[response.index("{"):response.rindex("}")+1]
            return json.loads(json_str)
    except:
        pass
    
    return {
        "subject": f"Quick question for {company}",
        "body": f"Hey {name.split()[0] if name else 'there'},\n\nI noticed {company} is doing solid work in {city}. Quick question - how are you handling after-hours calls?\n\nBased on your reviews, you might be missing ${monthly_loss:,.0f}/month in potential revenue.\n\nWould a 10-minute chat about AI phone agents be worth your time?"
    }


def create_email_html(prospect: Dict, message: Dict) -> str:
    """Create premium HTML email"""
    company = prospect.get("company_name", "Your Company")
    contact = prospect.get("contacts", [{}])[0]
    name = contact.get("name", "there").split()[0]
    savings = prospect.get("savings_analysis", {})
    monthly_loss = savings.get("monthly_lost_revenue", 10000)
    annual_savings = savings.get("net_annual_savings", 100000)
    roi = savings.get("roi_multiplier", 50)
    body = message.get("body", "")
    
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#0f172a;font-family:system-ui,sans-serif;">
<div style="max-width:600px;margin:0 auto;padding:40px 20px;">
    <div style="text-align:center;margin-bottom:30px;">
        <h1 style="color:#f8fafc;font-size:24px;margin:0;">AI Service Co</h1>
        <p style="color:#64748b;font-size:14px;margin:5px 0;">24/7 AI Phone Agents</p>
    </div>
    <div style="background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);border:1px solid #334155;border-radius:16px;padding:30px;margin-bottom:30px;">
        <p style="color:#f8fafc;font-size:18px;line-height:1.6;margin:0 0 20px 0;">Hey {name},</p>
        <p style="color:#94a3b8;font-size:16px;line-height:1.7;margin:0;">{body.replace(chr(10), '<br>')}</p>
    </div>
    <div style="background:#1e293b;border:1px solid #334155;border-radius:16px;overflow:hidden;margin-bottom:30px;">
        <a href="{VIDEO_URL}" target="_blank" style="display:block;position:relative;">
            <img src="https://i.ytimg.com/vi/C4GRQ8xaFn0/maxresdefault.jpg" alt="Watch" style="width:100%;height:auto;">
            <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:60px;height:60px;background:rgba(37,99,235,0.9);border-radius:50%;"></div>
        </a>
        <div style="padding:15px;text-align:center;">
            <p style="color:#60a5fa;font-size:13px;margin:0;">▶️ 45-sec demo: How we save ${monthly_loss:,.0f}/mo</p>
        </div>
    </div>
    <div style="background:linear-gradient(135deg,#14532d 0%,#166534 100%);border-radius:16px;padding:20px;margin-bottom:30px;text-align:center;">
        <p style="color:#4ade80;font-size:24px;font-weight:700;margin:0;">${annual_savings:,.0f}</p>
        <p style="color:#86efac;font-size:12px;margin:5px 0 0 0;">Your Est. Annual Savings | {roi}x ROI</p>
    </div>
    <div style="text-align:center;margin-bottom:30px;">
        <a href="{CALENDLY_LINK}" style="display:inline-block;background:linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%);color:white;text-decoration:none;padding:16px 35px;border-radius:12px;font-size:15px;font-weight:600;">
            📅 Book 10-Min Demo
        </a>
    </div>
    <div style="border-top:1px solid #334155;padding-top:20px;text-align:center;">
        <p style="color:#94a3b8;font-size:13px;margin:0;">Daniel | AI Service Co</p>
        <p style="color:#64748b;font-size:11px;margin:5px 0 0 0;">Reply or call (352) 936-8152</p>
    </div>
</div>
</body>
</html>"""


def run_intel_gathering():
    """Gather deep intel on 100 prospects"""
    print("=" * 70)
    print("🔍 DEEP INTEL GATHERING - 100 FLORIDA HVAC PROSPECTS")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)
    
    agent = DeepIntelAgent()
    all_prospects = []
    
    total = len(FLORIDA_HVAC_TARGETS)
    print(f"\n📡 Analyzing {total} HVAC companies across Florida...")
    
    for i, target in enumerate(FLORIDA_HVAC_TARGETS, 1):
        print(f"\n[{i}/{total}] {target['company']} ({target['city']})")
        
        try:
            dossier = agent.gather_intel(target["company"], target["city"], target["state"])
            savings = calculate_savings(dossier)
            dossier["savings_analysis"] = savings
            
            # Generate personalized message
            message = generate_message(dossier, savings)
            dossier["personalized_message"] = message
            
            # Priority score
            score = (
                savings["roi_multiplier"] * 10 +
                dossier.get("reviews", {}).get("google", {}).get("rating", 3) * 5 +
                100
            )
            dossier["priority_score"] = round(score, 1)
            
            all_prospects.append(dossier)
            print(f"    ✅ Score: {score:.0f} | Est. Loss: ${savings['monthly_lost_revenue']:,.0f}/mo")
            
        except Exception as e:
            print(f"    ❌ Failed: {e}")
    
    # Sort by priority
    all_prospects.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
    
    # Save
    os.makedirs("campaign_data", exist_ok=True)
    output_file = f"campaign_data/scaled_100_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, "w") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_prospects": len(all_prospects),
            "prospects": all_prospects
        }, f, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"📁 Intel saved: {output_file}")
    print(f"   Total prospects: {len(all_prospects)}")
    print("=" * 70)
    
    return output_file


def run_rate_limited_send(data_file: str = None):
    """Send emails with rate limiting (20 per 10 minutes)"""
    # Find latest data file
    if not data_file:
        files = sorted([f for f in os.listdir("campaign_data") if f.startswith("scaled_100")])
        if not files:
            print("❌ No prospect data found. Run with --intel first.")
            return
        data_file = os.path.join("campaign_data", files[-1])
    
    with open(data_file, "r") as f:
        data = json.load(f)
    
    prospects = data.get("prospects", [])
    
    print("=" * 70)
    print("📧 RATE-LIMITED EMAIL SEND")
    print(f"Prospects: {len(prospects)}")
    print(f"Rate limit: {RATE_LIMIT} emails per {RATE_WINDOW//60} minutes")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)
    
    results = {"sent": [], "failed": [], "timestamp": datetime.now().isoformat()}
    batch_count = 0
    
    for i, prospect in enumerate(prospects, 1):
        company = prospect.get("company_name", "Unknown")
        contacts = prospect.get("contacts", [])
        
        if not contacts:
            continue
        
        contact = contacts[0]
        email = contact.get("email")
        name = contact.get("name", "Unknown")
        
        if not email:
            continue
        
        # Rate limiting
        if batch_count >= RATE_LIMIT:
            print(f"\n⏸️ Rate limit reached. Waiting {RATE_WINDOW//60} minutes...")
            time.sleep(RATE_WINDOW)
            batch_count = 0
            print("▶️ Resuming...\n")
        
        message = prospect.get("personalized_message", {"subject": f"Question for {company}", "body": ""})
        html = create_email_html(prospect, message)
        
        print(f"[{i}/{len(prospects)}] 📧 {company} -> {email}")
        
        try:
            resend.Emails.send({
                "from": "Daniel <daniel@aiserviceco.com>",
                "to": [email],
                "reply_to": "owner@aiserviceco.com",
                "subject": message.get("subject", f"Question for {company}"),
                "html": html
            })
            results["sent"].append({"company": company, "email": email})
            print(f"    ✅ Sent!")
            batch_count += 1
            
        except Exception as e:
            results["failed"].append({"company": company, "email": email, "error": str(e)})
            print(f"    ❌ {e}")
    
    # Save log
    log_file = f"campaign_logs/scaled_send_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("campaign_logs", exist_ok=True)
    with open(log_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"✅ Sent: {len(results['sent'])} | ❌ Failed: {len(results['failed'])}")
    print(f"📁 Log: {log_file}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaled HVAC Campaign")
    parser.add_argument("--intel", action="store_true", help="Gather intel only")
    parser.add_argument("--send", action="store_true", help="Send emails (rate limited)")
    parser.add_argument("--all", action="store_true", help="Intel + Send")
    args = parser.parse_args()
    
    if args.intel or args.all:
        data_file = run_intel_gathering()
    
    if args.send or args.all:
        run_rate_limited_send()
