"""
EMERGENCY PROSPECTING: Traffic Light Email Format
Matches Dan's proven template exactly
"""
import os
import httpx
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "***REMOVED***")

# Real Lakeland FL businesses
LAKELAND_TARGETS = [
    {"name": "Lakeland Roofing Company", "website": "lakelandroofing.com", "industry": "Roofing"},
    {"name": "All Pro Roofing", "website": "allproroofingfl.com", "industry": "Roofing"},
    {"name": "Precision Roofing Lakeland", "website": "precisionroofinglakeland.com", "industry": "Roofing"},
    {"name": "Scott's Air Conditioning", "website": "scottsair.com", "industry": "HVAC"},
    {"name": "Air Pros USA", "website": "airprosusa.com", "industry": "HVAC"},
    {"name": "Lakeland Air Conditioning", "website": "lakelandac.com", "industry": "HVAC"},
    {"name": "Viper Auto Care", "website": "viperautocare.com", "industry": "Auto Repair"},
    {"name": "Honest 1 Auto Care Lakeland", "website": "honest1lakeland.com", "industry": "Auto Repair"},
    {"name": "Premium Auto Repair", "website": "premiumautorepairlakeland.com", "industry": "Auto Repair"},
    {"name": "ABC Plumbing Lakeland", "website": "abcplumbinglakeland.com", "industry": "Plumbing"},
    {"name": "Roto-Rooter Lakeland", "website": "rotorooter.com", "industry": "Plumbing"},
    {"name": "Lakeland Lawn Services", "website": "lakelandlawnservices.com", "industry": "Landscaping"},
    {"name": "Green Thumb Landscaping", "website": "greenthumb-lakeland.com", "industry": "Landscaping"},
    {"name": "ProCuts Lawn Care", "website": "procutslawncare.com", "industry": "Landscaping"},
    {"name": "Polk County Electric", "website": "polkcountyelectric.com", "industry": "Electrical"},
]


def find_email_hunter(domain: str) -> dict:
    """Use Hunter.io to find email for domain"""
    url = "https://api.hunter.io/v2/domain-search"
    params = {"domain": domain, "api_key": HUNTER_API_KEY}
    
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(url, params=params)
            data = resp.json()
            
            emails = data.get("data", {}).get("emails", [])
            if emails:
                best = max(emails, key=lambda x: x.get("confidence", 0))
                return {
                    "email": best.get("value"),
                    "first_name": best.get("first_name", ""),
                    "last_name": best.get("last_name", ""),
                    "position": best.get("position", ""),
                    "confidence": best.get("confidence", 0)
                }
            
            pattern = data.get("data", {}).get("pattern")
            if pattern:
                return {"email": f"info@{domain}", "pattern": pattern, "confidence": 50}
    except Exception as e:
        print(f"  Error: {e}")
    
    return {"email": f"info@{domain}", "confidence": 30, "fallback": True}


def generate_traffic_light_email(lead: dict) -> str:
    """Generate email in Dan's proven Traffic Light format"""
    
    # Personalized greeting
    first_name = lead.get("first_name", "")
    last_name = lead.get("last_name", "")
    
    if first_name and last_name:
        greeting = f"Dear {first_name},"
    elif last_name:
        greeting = f"Dear Mr./Ms. {last_name},"
    else:
        greeting = "Dear Business Owner,"
    
    company = lead["name"]
    website = lead["website"]
    industry = lead["industry"]
    
    # Industry-specific issues for the traffic light table
    issues = {
        "Roofing": {
            "critical": "The desktop site may be failing Google's Core Web Vitals standards, acting as a 'hidden penalty' that makes it harder for homeowners to find you during storm season.",
            "warning": "The site may be missing a dedicated Privacy Policy. Under the Florida Digital Bill of Rights, this is a mandatory requirement for businesses collecting customer data via contact forms.",
            "opportunity": "Currently, your team may be manually filtering every roofing inquiry. An AI-powered intake system could pre-qualify leads, ensuring your crews only spend time on high-value jobs."
        },
        "HVAC": {
            "critical": "The desktop site may be failing Google's performance standards, creating a 'hidden penalty' that makes it harder for customers to find you when their AC breaks down.",
            "warning": "The site may be missing a dedicated Privacy Policy. Under the Florida Digital Bill of Rights, this is mandatory for businesses collecting customer data via web forms.",
            "opportunity": "Currently, your staff may be manually fielding every inquiry. An intelligent intake system could pre-screen calls, ensuring your technicians only respond to qualified service calls."
        },
        "Auto Repair": {
            "critical": "The desktop site may be underperforming on Google's speed metrics, making it harder for drivers to find you when they need urgent repairs.",
            "warning": "The site may lack proper legal disclosures. Under Florida regulations, businesses collecting customer data must have visible Privacy Policies.",
            "opportunity": "Your team may be manually processing every inquiry. Automated lead screening could save hours of phone time and prioritize high-value repair jobs."
        },
        "Plumbing": {
            "critical": "The site may be failing Google's performance checklist, meaning emergency plumbing customers might not find you in search results when pipes burst.",
            "warning": "Missing legal compliance pages could expose the business to regulatory issues under Florida's consumer protection laws.",
            "opportunity": "Manual call handling means your plumbers spend time on unqualified leads. AI intake could filter for genuine emergency calls."
        },
        "Landscaping": {
            "critical": "The website may be loading slowly, causing potential customers to choose competitors who appear higher in local search results.",
            "warning": "The site may be missing essential legal pages that Florida requires for businesses collecting customer information online.",
            "opportunity": "An automated lead system could help separate tire-kickers from serious landscaping projects, protecting your crew's valuable time."
        },
        "Electrical": {
            "critical": "The desktop site may not meet Google's performance standards, potentially hiding your business from customers searching for electricians.",
            "warning": "Missing Privacy Policy could create compliance issues under Florida's Digital Bill of Rights.",
            "opportunity": "Automated screening could help prioritize emergency electrical calls over routine inquiries."
        }
    }
    
    issue = issues.get(industry, issues["HVAC"])
    
    email = f"""Subject: {company} - Digital Performance Audit Results

{greeting}

I am a local digital strategist here in Lakeland, and I've conducted a brief health audit of {company}'s online presence.

To save you time, I have summarized the three critical areas that currently impact your online reputation, search ranking, and lead flow:

AREA                 STATUS              THE RISK TO THE BUSINESS
---------------------------------------------------------------------------
Search Visibility    CRITICAL (RED)      {issue['critical']}

Legal Compliance     WARNING (YELLOW)    {issue['warning']}

Lead Efficiency      OPPORTUNITY         {issue['opportunity']}

THE SOLUTION: I specialize in helping {industry.lower()} businesses bridge these technical gaps. I would like to offer {company} a 14-day "Intelligent Intake" trial. We can install a digital assistant on your site that "pre-screens" potential clients before they ever call your office - ensuring your team only spends time on high-value cases.

MY LOCAL GUARANTEE: Because I am a local Lakeland resident, I would like to fix your Search Visibility (Google Failure) for free this week. This will move your site back into the "Green" zone and allow you to see the quality of my work firsthand with zero risk to the business.

I will follow up with your office in an hour to see if you have any questions.

Best regards,

Daniel Coffman
352-936-8152
Owner, AI Service Co
www.aiserviceco.com
"""
    return email


def run_traffic_light_prospecting():
    """Main workflow using Traffic Light format"""
    print("\n" + "=" * 70)
    print("TRAFFIC LIGHT EMAIL GENERATOR - Dan's Proven Format")
    print(f"Time: {datetime.now().strftime('%I:%M %p')}")
    print("=" * 70)
    
    enriched_leads = []
    
    for biz in LAKELAND_TARGETS[:15]:
        print(f"\n{biz['name']} ({biz['website']})")
        email_data = find_email_hunter(biz["website"])
        
        if email_data and email_data.get("email"):
            lead = {**biz, **email_data}
            enriched_leads.append(lead)
            
            if email_data.get("first_name"):
                print(f"   Email: {email_data['email']} (Contact: {email_data.get('first_name', '')} {email_data.get('last_name', '')})")
            else:
                print(f"   Email: {email_data['email']}")
    
    print("\n" + "=" * 70)
    print(f"ENRICHMENT RESULTS: {len(enriched_leads)} leads with emails")
    print("=" * 70)
    
    # Generate email drafts
    print("\nGENERATING TRAFFIC LIGHT EMAILS...\n")
    
    drafts = []
    for lead in enriched_leads[:10]:
        draft = generate_traffic_light_email(lead)
        drafts.append({
            "to": lead["email"],
            "company": lead["name"],
            "contact": f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip(),
            "draft": draft
        })
        contact_info = f" (Contact: {lead.get('first_name', '')})" if lead.get('first_name') else ""
        print(f"Draft ready: {lead['name']}{contact_info}")
    
    # Save drafts to file
    output_file = "email_drafts_for_review.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Email Drafts for Dan's Review - Traffic Light Format\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}\n\n")
        f.write("---\n\n")
        
        for i, d in enumerate(drafts, 1):
            contact_note = f" | Contact: {d['contact']}" if d['contact'] else ""
            f.write(f"## Email {i}: {d['company']}{contact_note}\n")
            f.write(f"**To:** {d['to']}\n\n")
            f.write("```\n")
            f.write(d['draft'])
            f.write("```\n\n")
            f.write("---\n\n")
    
    print(f"\nSaved {len(drafts)} email drafts to: {output_file}")
    print("\nNEXT: Open email_drafts_for_review.md and review!")
    
    return drafts


if __name__ == "__main__":
    run_traffic_light_prospecting()
