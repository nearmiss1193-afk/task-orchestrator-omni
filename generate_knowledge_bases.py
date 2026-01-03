import os
import json

INDUSTRIES = {
    "HVAC": {
        "services": ["AC Repair", "Furnace Install", "Duct Cleaning", "Emergency Fix"],
        "pricing": "Diagnostic: $89 (Waived with repair). Tune-up: $129. New System: Start at $4,500.",
        "script": "Cooling Cal here. Is your AC blowing hot air or making a weird noise?"
    },
    "Plumber": {
        "services": ["Leak Repair", "Water Heater", "Drain Cleaning", "Pipe Burst"],
        "pricing": "Dispatch Fee: $69. Drain Clear: $199. Water Heater: Starts at $1,200.",
        "script": "Dispatch Dan speaking. Is this an emergency leak or a clogged drain?"
    },
    "Roofer": {
        "services": ["Roof Inspection", "Shingle Repair", "Full Replacement", "Gutter Guard"],
        "pricing": "Inspection: Free (Storm Special). Repair: Approx $500/sq. Full Roof: Custom Quote.",
        "script": "Estimator Eric here. Did storm damage catch you, or is this just old age?"
    },
    "Electrician": {
        "services": ["Panel Upgrade", "Outlet Repair", "EV Charger", "Lighting"],
        "pricing": "Trip Charge: $99. Panel Swap: $2,500+. EV Charger: $800+ install.",
        "script": "Electrician Ellie. Did the breaker trip or are you looking to upgrade?"
    },
    "Solar": {
        "services": ["Solar Install", "Battery Backup", "System Audit", "Panel Cleaning"],
        "pricing": "$0 Down Financing. ROI in 7-9 years. Tax Credit: 30%.",
        "script": "Sunny Sam. Are you looking to kill your electric bill or just get grid independence?"
    },
    "Landscaping": {
        "services": ["Mowing", "Hardscaping", "Tree Trimming", "Irrigation"],
        "pricing": "Mow: $50/visit. Spring Cleanup: $400. Design: Custom.",
        "script": "Green Thumb Gary. Do you need a weekly mow or a full backyard makeover?"
    },
    "Pest": {
        "services": ["Termite", "Ants/Spiders", "Rodent Exclusion", "Bed Bugs"],
        "pricing": "Quarterly Plan: $129/qtr. One-time: $249. Termite: Quote required.",
        "script": "Exterminator Ed. What's crawling in your house that shouldn't be?"
    },
    "Cleaning": {
        "services": ["Deep Clean", "Standard Clean", "Move-in/out", "Office Clean"],
        "pricing": "Standard: $150 (3 bed). Deep: $300. Hourly: $45/hr/cleaner.",
        "script": "Maid Mary. Do you need a deep reset or just a maintenance sparkle?"
    },
    "Restoration": {
        "services": ["Water Mitigation", "Mold Remediation", "Fire Cleanup", "Reconstruction"],
        "pricing": "Insurance Billing (Direct). Deductible Assistance Available.",
        "script": "Flood Phil. Is there standing water right now? I can have a crew in 60 mins."
    },
    "AutoDetail": {
        "services": ["Interior Detail", "Ceramic Coating", "Paint Correction", "Mobile Wash"],
        "pricing": "Full Detail: $250. Ceramic: $800+. Maintenance Wash: $80.",
        "script": "Detail Dave. You want the interior fresh or the paint popping?"
    }
}

def generate_kb():
    print("🧠 Injecting Empire Knowledge Bases...")
    os.makedirs("modules/knowledge", exist_ok=True)
    
    for industry, data in INDUSTRIES.items():
        filename = f"modules/knowledge/{industry.lower()}_kb.md"
        content = f"""# {industry} Knowledge Base & Script
        
## AGENT IDENTITY
- **Name**: {data['script'].split(' ')[0]} {data['script'].split(' ')[1]}
- **Role**: AI Dispatcher & Sales Coordinator
- **Tone**: Professional, Empathetic, Efficiency-Focused (Spartan Standard)

## OPENING SCRIPT
"{data['script']}"

## SERVICE MENU
{chr(10).join(['- ' + s for s in data['services']])}

## PRICING CHEAT SHEET
{data['pricing']}

## OBJECTION HANDLING
- **"Is this a robot?"**: "I'm an AI assistant helping the team get to you faster. I can book an appointment instantly. Does that work?"
- **"Can I talk to a human?"**: "Everyone is on a job right now (that's why I'm here!). I can flag this as urgent for a call back, or book a slot now. Which do you prefer?"

## BOOKING PROTOCOL
1. Qualify the Issue (Emergency vs Routine).
2. Quote Base Pricing (if applicable).
3. Send Booking Link (SMS) or Book Directly.
"""
        with open(filename, "w") as f:
            f.write(content)
        print(f"✅ Generated: {filename}")

if __name__ == "__main__":
    generate_kb()
