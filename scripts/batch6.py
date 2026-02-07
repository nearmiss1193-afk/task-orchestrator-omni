"""
Batch 6 - HVAC/Trades prospects - FULLY PERSONALIZED
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from send_live_outreach import send_batch

# BATCH 6 - HVAC and Trades
BATCH_6 = [
    {
        "business": "One Hour Air Conditioning",
        "industry": "HVAC",
        "url": "https://www.onehourairbrandon.com/",
        "email": "info@onehourairbrandon.com",
        "contact_name": "Brandon",  # Branch location name as personalization
        "liability_issues": ["Emergency calls cause overflow.", "Privacy/terms not obvious."],
        "performance_issues": ["PageSpeed needs optimization.", "After-hours leads missed."],
        "growth_opps": ["24/7 AI Receptionist – never miss emergency calls", "SMS follow-ups", "Compliance upgrades"],
        "speed_score": 62
    },
    {
        "business": "Airmasters of Tampa Bay",
        "industry": "HVAC",
        "url": "https://airmasters.net/",
        "email": "info@airmasters.net",
        "contact_name": "Mike",
        "liability_issues": ["No visible consent.", "High seasonal demand causes missed calls."],
        "performance_issues": ["PageSpeed could improve.", "Lead capture limited."],
        "growth_opps": ["24/7 AI Receptionist", "SMS automation", "Digital ads"],
        "speed_score": 64
    },
    {
        "business": "Town & Country Air",
        "industry": "HVAC",
        "url": "https://towncountryair.com/",
        "email": "info@towncountryair.com",
        "contact_name": "Tom",
        "liability_issues": ["No consent checkbox.", "Manual quoting process."],
        "performance_issues": ["PageSpeed needs improvement.", "Mobile experience limited."],
        "growth_opps": ["24/7 AI Receptionist", "Omnichannel communications", "Review automation"],
        "speed_score": 66
    },
    {
        "business": "Tri-County Air & Plumbing",
        "industry": "HVAC/Plumbing",
        "url": "https://tricountyair.com/",
        "email": "info@tricountyair.com",
        "contact_name": "Chris",
        "liability_issues": ["Contact form lacks consent.", "High after-hours emergency calls."],
        "performance_issues": ["PageSpeed could be optimized.", "Mobile booking limited."],
        "growth_opps": ["24/7 AI Receptionist – capture emergencies", "SMS automation", "Compliance fixes"],
        "speed_score": 60
    },
    {
        "business": "ServiceOne Air Conditioning",
        "industry": "HVAC",
        "url": "https://www.serviceoneac.com/",
        "email": "info@serviceoneac.com",
        "contact_name": "Dave",
        "liability_issues": ["Phone-only booking.", "Privacy policy not evident."],
        "performance_issues": ["PageSpeed needs optimization.", "After-hours missed."],
        "growth_opps": ["24/7 AI Receptionist", "Compliance pages", "Review automation"],
        "speed_score": 64
    }
]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        print("🚀 SENDING BATCH 6 LIVE - HVAC/TRADES")
        send_batch(BATCH_6, live=True)
    else:
        print("📧 SENDING BATCH 6 PREVIEWS TO OWNER")
        send_batch(BATCH_6, live=False)
