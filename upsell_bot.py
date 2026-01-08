"""
UPSELL BOT
==========
Sarah suggests add-ons during calls (maintenance plans, etc.)
"""
import os
import json
from datetime import datetime

# Upsell triggers and recommendations
UPSELL_RULES = {
    "ac_repair": {
        "upsells": ["Maintenance Plan ($29/mo)", "Duct Cleaning ($199)", "Smart Thermostat ($149 installed)"],
        "trigger_phrases": ["old unit", "keeps breaking", "high bills", "not cooling"],
        "script": "By the way, since we're already there, would you be interested in {upsell}? It could save you money long-term."
    },
    "furnace_repair": {
        "upsells": ["Annual Tune-Up Package ($199)", "Carbon Monoxide Detector ($89)", "Air Quality Test ($49)"],
        "trigger_phrases": ["old furnace", "smells weird", "yellow flame"],
        "script": "I'd also recommend {upsell} - it's something we offer to keep your family safe."
    },
    "plumbing": {
        "upsells": ["Drain Cleaning ($149)", "Water Heater Flush ($99)", "Whole-Home Inspection ($199)"],
        "trigger_phrases": ["slow drain", "old pipes", "water heater"],
        "script": "While we're there, we can also do {upsell} - it prevents bigger problems down the road."
    },
    "roofing": {
        "upsells": ["Gutter Cleaning ($149)", "Attic Insulation Check ($49)", "Roof Coating ($499+)"],
        "trigger_phrases": ["leak", "old roof", "storm damage"],
        "script": "To prevent future issues, might I suggest {upsell}? It's great protection for your investment."
    }
}

# Maintenance plan details
MAINTENANCE_PLANS = {
    "basic": {
        "name": "Basic Care",
        "price": "$19/mo or $199/yr",
        "includes": ["Annual tune-up", "Priority scheduling", "10% parts discount"],
        "pitch": "For just $19/month, you get peace of mind with annual tune-ups and priority service when you need us."
    },
    "premium": {
        "name": "Premium Protection",
        "price": "$39/mo or $399/yr",
        "includes": ["2 tune-ups/year", "Priority scheduling", "20% discount on all services", "No overtime fees", "Free diagnostic calls"],
        "pitch": "Our Premium plan at $39/month covers everything - two tune-ups, 20% off all work, and no overtime charges."
    },
    "vip": {
        "name": "VIP Complete",
        "price": "$69/mo or $699/yr",
        "includes": ["Unlimited tune-ups", "Same-day priority", "30% discount", "Extended warranty", "Dedicated technician"],
        "pitch": "Our VIP plan gives you a dedicated tech who knows your system, unlimited tune-ups, and 30% off everything."
    }
}


def detect_upsell_opportunity(call_transcript: str, service_type: str = "ac_repair") -> dict:
    """Detect upsell opportunities from call transcript"""
    
    transcript_lower = call_transcript.lower()
    rules = UPSELL_RULES.get(service_type, UPSELL_RULES["ac_repair"])
    
    opportunities = []
    
    # Check for trigger phrases
    for phrase in rules["trigger_phrases"]:
        if phrase in transcript_lower:
            for upsell in rules["upsells"]:
                opportunities.append({
                    "trigger": phrase,
                    "upsell": upsell,
                    "script": rules["script"].format(upsell=upsell)
                })
            break
    
    # Always offer maintenance plan if not on one
    if "maintenance plan" not in transcript_lower and "already have a plan" not in transcript_lower:
        opportunities.append({
            "trigger": "no_maintenance_plan",
            "upsell": "Maintenance Plan",
            "script": MAINTENANCE_PLANS["premium"]["pitch"]
        })
    
    return {
        "service_type": service_type,
        "opportunities": opportunities,
        "detected_at": datetime.now().isoformat()
    }


def generate_upsell_injection(opportunity: dict) -> str:
    """Generate text for Sarah to inject into conversation"""
    return opportunity.get("script", "")


def get_maintenance_pitch(plan_type: str = "premium") -> str:
    """Get maintenance plan pitch for Sarah"""
    plan = MAINTENANCE_PLANS.get(plan_type, MAINTENANCE_PLANS["premium"])
    return plan["pitch"]


if __name__ == "__main__":
    # Test
    test_transcript = """
    Customer: My AC unit is about 15 years old and it keeps breaking down.
    Sarah: I understand, that's frustrating. Let me get a tech out there to help.
    """
    
    result = detect_upsell_opportunity(test_transcript, "ac_repair")
    print(json.dumps(result, indent=2))
    
    for opp in result["opportunities"]:
        print(f"\n🎯 Upsell: {opp['upsell']}")
        print(f"   Script: {opp['script']}")
