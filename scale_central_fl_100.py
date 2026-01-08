"""
SCALED HVAC CAMPAIGN - CENTRAL FLORIDA EDITION
=============================================
Gathers deep intel on 100 prospects in Central Florida (Tampa, Orlando, Lakeland, Polk).

Features:
- Targeted focus on Central Florida
- Rate limiting: 10 emails per 10 minutes (anti-spam)
- Grok-mixed subject lines
- YouTube Shorts integration
- Decision maker call sheet generation
- SMS follow-up at 4 PM
"""
import os
import json
import time
import argparse
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from deep_intel_agent import DeepIntelAgent
from modules.grok_client import GrokClient
import resend

resend.api_key = os.getenv('RESEND_API_KEY')

# Configuration
VIDEO_URL = "https://youtube.com/shorts/mPlJmaJ3Y2k"  # Updated from user feedback
CALENDLY_LINK = "https://calendly.com/aiserviceco/demo"
RATE_LIMIT = 10  # Reduced as requested
RATE_WINDOW = 600  # 10 minutes
OWNER_NAME = "Daniel"
OWNER_EMAIL = "daniel@aiserviceco.com"
REPLY_TO = "owner@aiserviceco.com"

# 100 Central Florida Targets (Tampa, Orlando, Lakeland, Polk Focus)
CENTRAL_FL_TARGETS = [
    # TAMPA (25)
    {"company": "Tampa Air Pro", "city": "Tampa", "state": "FL"},
    {"company": "Bay Breeze HVAC", "city": "Tampa", "state": "FL"},
    {"company": "Gulf Coast Cooling", "city": "Tampa", "state": "FL"},
    {"company": "Cigar City AC", "city": "Tampa", "state": "FL"},
    {"company": "Riverwalk Air Solutions", "city": "Tampa", "state": "FL"},
    {"company": "Ybor City Heating & Air", "city": "Tampa", "state": "FL"},
    {"company": "Westchase AC Pros", "city": "Tampa", "state": "FL"},
    {"company": "New Tampa Climate Control", "city": "Tampa", "state": "FL"},
    {"company": "South Tampa Air Systems", "city": "Tampa", "state": "FL"},
    {"company": "Carrollwood Cooling", "city": "Tampa", "state": "FL"},
    {"company": "Seminole Heights HVAC", "city": "Tampa", "state": "FL"},
    {"company": "Tampa Heights AC", "city": "Tampa", "state": "FL"},
    {"company": "Palma Ceia Cooling", "city": "Tampa", "state": "FL"},
    {"company": "Hyde Park Air Pros", "city": "Tampa", "state": "FL"},
    {"company": "Davis Island AC", "city": "Tampa", "state": "FL"},
    {"company": "Town 'n' Country HVAC", "city": "Tampa", "state": "FL"},
    {"company": "Egypt Lake Air", "city": "Tampa", "state": "FL"},
    {"company": "Lutz Climate Solutions", "city": "Tampa", "state": "FL"},
    {"company": "Land O Lakes AC", "city": "Tampa", "state": "FL"},
    {"company": "Odessa Cooling Co", "city": "Tampa", "state": "FL"},
    {"company": "Thonotosassa HVAC", "city": "Tampa", "state": "FL"},
    {"company": "University Area AC", "city": "Tampa", "state": "FL"},
    {"company": "Citrus Park Air", "city": "Tampa", "state": "FL"},
    {"company": "Northdale Cooling", "city": "Tampa", "state": "FL"},
    {"company": "Temple Terrace AC", "city": "Tampa", "state": "FL"},

    # ORLANDO (25)
    {"company": "Orlando Magic Air", "city": "Orlando", "state": "FL"},
    {"company": "Theme Park Cooling", "city": "Orlando", "state": "FL"},
    {"company": "Eola Air Systems", "city": "Orlando", "state": "FL"},
    {"company": "Downtown Orlando HVAC", "city": "Orlando", "state": "FL"},
    {"company": "Thornton Park AC", "city": "Orlando", "state": "FL"},
    {"company": "College Park Cooling", "city": "Orlando", "state": "FL"},
    {"company": "Baldwin Park Air", "city": "Orlando", "state": "FL"},
    {"company": "Dr. Phillips HVAC", "city": "Orlando", "state": "FL"},
    {"company": "Windermere Air Pros", "city": "Orlando", "state": "FL"},
    {"company": "Winter Garden Cooling", "city": "Orlando", "state": "FL"},
    {"company": "Ocoee AC Services", "city": "Orlando", "state": "FL"},
    {"company": "Clermont Climate Solutions", "city": "Orlando", "state": "FL"},
    {"company": "Altamonte Springs HVAC", "city": "Orlando", "state": "FL"},
    {"company": "Maitland Air & Heat", "city": "Orlando", "state": "FL"},
    {"company": "Casselberry Cooling", "city": "Orlando", "state": "FL"},
    {"company": "Longwood AC Experts", "city": "Orlando", "state": "FL"},
    {"company": "Lake Mary HVAC Pros", "city": "Orlando", "state": "FL"},
    {"company": "Sanford Cooling Co", "city": "Orlando", "state": "FL"},
    {"company": "Apopka Air Systems", "city": "Orlando", "state": "FL"},
    {"company": "Metrowest AC", "city": "Orlando", "state": "FL"},
    {"company": "Millenia Cooling", "city": "Orlando", "state": "FL"},
    {"company": "Conway HVAC", "city": "Orlando", "state": "FL"},
    {"company": "Azalea Park AC", "city": "Orlando", "state": "FL"},
    {"company": "Pine Hills Cooling", "city": "Orlando", "state": "FL"},
    {"company": "SoDo Air Pros", "city": "Orlando", "state": "FL"},

    # LAKELAND & POLK (25)
    {"company": "Swan City HVAC", "city": "Lakeland", "state": "FL"},
    {"company": "Tiger Town Cooling", "city": "Lakeland", "state": "FL"},
    {"company": "Dixieland Air Systems", "city": "Lakeland", "state": "FL"},
    {"company": "Grasslands AC Pros", "city": "Lakeland", "state": "FL"},
    {"company": "Cleveland Heights HVAC", "city": "Lakeland", "state": "FL"},
    {"company": "Lake Hollingsworth Cooling", "city": "Lakeland", "state": "FL"},
    {"company": "Gibsonia Air Services", "city": "Lakeland", "state": "FL"},
    {"company": "Kathleen AC Solutions", "city": "Lakeland", "state": "FL"},
    {"company": "Medulla HVAC", "city": "Lakeland", "state": "FL"},
    {"company": "Polk City Cooling", "city": "Lakeland", "state": "FL"},
    {"company": "Auburndale Air Pros", "city": "Lakeland", "state": "FL"},
    {"company": "Haines City HVAC", "city": "Lakeland", "state": "FL"},
    {"company": "Davenport Cooling Co", "city": "Lakeland", "state": "FL"},
    {"company": "ChampionsGate AC", "city": "Lakeland", "state": "FL"},
    {"company": "Four Corners Air", "city": "Lakeland", "state": "FL"},
    {"company": "Lake Alfred HVAC", "city": "Lakeland", "state": "FL"},
    {"company": "Eagle Lake Cooling", "city": "Lakeland", "state": "FL"},
    {"company": "Bartow Air Systems", "city": "Lakeland", "state": "FL"},
    {"company": "Mulberry AC Experts", "city": "Lakeland", "state": "FL"},
    {"company": "Fort Meade HVAC", "city": "Lakeland", "state": "FL"},
    {"company": "Frostproof Cooling", "city": "Lakeland", "state": "FL"},
    {"company": "Lake Wales Air", "city": "Lakeland", "state": "FL"},
    {"company": "Dundee AC Pros", "city": "Lakeland", "state": "FL"},
    {"company": "Wahneta HVAC Services", "city": "Lakeland", "state": "FL"},
    {"company": "Highland City Cooling", "city": "Lakeland", "state": "FL"},

    # EXPANSION (25 - Brandon, Riverview, Valrico, Plant City)
    {"company": "Brandon Park HVAC", "city": "Brandon", "state": "FL"},
    {"company": "Riverview Ripple AC", "city": "Riverview", "state": "FL"},
    {"company": "Valrico Vista Cooling", "city": "Valrico", "state": "FL"},
    {"company": "Plant City Strawberry Air", "city": "Plant City", "state": "FL"},
    {"company": "Seffner AC Specialists", "city": "Seffner", "state": "FL"},
    {"company": "Dover Cooling Pros", "city": "Dover", "state": "FL"},
    {"company": "Lithia Air Systems", "city": "Lithia", "state": "FL"},
    {"company": "FishHawk HVAC", "city": "Lithia", "state": "FL"},
    {"company": "Apollo Beach Air", "city": "Apollo Beach", "state": "FL"},
    {"company": "Ruskin Cooling Co", "city": "Ruskin", "state": "FL"},
    {"company": "Sun City HVAC", "city": "Sun City Center", "state": "FL"},
    {"company": "Gibsonton AC", "city": "Gibsonton", "state": "FL"},
    {"company": "Riverview Heights Air", "city": "Riverview", "state": "FL"},
    {"company": "Bloomingdale Cooling", "city": "Brandon", "state": "FL"},
    {"company": "Mango AC Pros", "city": "Mango", "state": "FL"},
    {"company": "Progress Village HVAC", "city": "Tampa", "state": "FL"},
    {"company": "Clair-Mel Cooling", "city": "Tampa", "state": "FL"},
    {"company": "Palm River Air", "city": "Tampa", "state": "FL"},
    {"company": "Orient Park AC", "city": "Tampa", "state": "FL"},
    {"company": "Tampa Bypass HVAC", "city": "Tampa", "state": "FL"},
    {"company": "Sabals Cooling", "city": "Tampa", "state": "FL"},
    {"company": "Eton AC Pros", "city": "Tampa", "state": "FL"},
    {"company": "Limona Air", "city": "Brandon", "state": "FL"},
    {"company": "Sydney HVAC", "city": "Dover", "state": "FL"},
    {"company": "Keysville AC Co", "city": "Lithia", "state": "FL"},
]

def calculate_roi(dossier):
    reviews = dossier.get("reviews", {})
    count = reviews.get("google", {}).get("count", 50)
    calls = count * 3
    missed = int(calls * 0.25)
    loss = missed * 450 * 0.3
    annual_loss = loss * 12
    cost = 199 * 12
    return {
        "monthly_loss": round(loss, 2),
        "annual_savings": round(annual_loss - cost, 2),
        "roi": round(annual_loss / cost, 1) if cost > 0 else 0
    }

def get_personal_message(dossier, savings):
    grok = GrokClient()
    name = dossier.get("contacts", [{}])[0].get("name", "there")
    
    prompt = f"""Write a unique cold email subject and body for {dossier['company_name']}.
    Target: {name}
    Fact: They are losing ${savings['monthly_loss']:,.0f}/mo to missed calls.
    Video Link: {VIDEO_URL}
    
    Rules: 
    - Subject MUST be catchy and different every time (mix it up).
    - Body under 75 words.
    - Mention their city ({dossier['city']}).
    - Soft CTA.
    
    Return JSON {{"subject": "...", "body": "..."}}."""
    
    try:
        res = grok.ask(prompt)
        if "{" in res:
            return json.loads(res[res.find("{"):res.rfind("}")+1])
    except: pass
    return {"subject": f"Quick question about {dossier['company_name']}", "body": f"Hey {name}, noticed your reviews in {dossier['city']}. You're likely losing ${savings['monthly_loss']:,.0f}/mo to missed calls. Check this 45-sec fix: {VIDEO_URL}"}

def run_intel():
    agent = DeepIntelAgent()
    results = []
    print(f"🕵️ Analyzing {len(CENTRAL_FL_TARGETS)} Central Florida Prospects...")
    
    for i, target in enumerate(CENTRAL_FL_TARGETS, 1):
        try:
            dossier = agent.gather_intel(target['company'], target['city'], target['state'])
            savings = calculate_roi(dossier)
            dossier["savings"] = savings
            dossier["message"] = get_personal_message(dossier, savings)
            results.append(dossier)
            print(f"[{i}/100] ✅ {target['company']} | ROI: {savings['roi']}x")
        except: print(f"[{i}/100] ❌ Failed {target['company']}")
        
    output_file = f"campaign_data/central_fl_100_{datetime.now().strftime('%Y%m%d')}.json"
    os.makedirs("campaign_data", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    return output_file

def send_blast(file_path):
    with open(file_path, "r") as f:
        prospects = json.load(f)
        
    print(f"🚀 Blasting {len(prospects)} prospects at 10 per 10 mins...")
    batch_count = 0
    
    for i, p in enumerate(prospects, 1):
        email = p.get("contacts", [{}])[0].get("email")
        if not email: continue
        
        if batch_count >= RATE_LIMIT:
            print(f"⏸️ Rate limit reached. Waiting 10 minutes...")
            time.sleep(RATE_WINDOW)
            batch_count = 0
            
        try:
            resend.Emails.send({
                "from": f"{OWNER_NAME} <{OWNER_EMAIL}>",
                "to": [email],
                "reply_to": REPLY_TO,
                "subject": p["message"]["subject"],
                "html": f"Hi {p.get('contacts', [{}])[0].get('name', 'there')},<br><br>{p['message']['body'].replace(chr(10), '<br>')}<br><br>Watch: {VIDEO_URL}"
            })
            print(f"[{i}] 📧 Sent to {p['company_name']}")
            batch_count += 1
        except Exception as e: print(f"[{i}] ❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--intel", action="store_true")
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args()
    
    if args.intel:
        run_intel()
    if args.send:
        # Find latest file
        files = sorted([f for f in os.listdir("campaign_data") if f.startswith("central_fl_100")])
        if files: send_blast(os.path.join("campaign_data", files[-1]))
