"""
Batch 5 - Next 5 prospects - FULLY PERSONALIZED
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from send_live_outreach import send_batch

# BATCH 5 - More prospects from extended list
BATCH_5 = [
    {
        "business": "Dolman Law Group",
        "industry": "Personal Injury Law",
        "url": "https://www.dolmanlaw.com/",
        "email": "info@dolmanlaw.com",
        "contact_name": "Matthew Dolman",  # VERIFIED from list
        "liability_issues": ["Contact form lacks TCPA consent.", "High call volume without opt-in."],
        "performance_issues": ["PageSpeed needs optimization.", "Competitive market requires speed."],
        "growth_opps": ["24/7 AI Receptionist – never miss case intake", "Client follow-up automation", "Google Maps optimization"],
        "speed_score": 60
    },
    {
        "business": "Burnetti P.A.",
        "industry": "Personal Injury Law",
        "url": "https://www.burnetti.com/",
        "email": "info@burnetti.com",
        "contact_name": "Doug Burnetti",  # VERIFIED from list
        "liability_issues": ["Website lacks consent checkbox.", "Calls go unanswered after hours."],
        "performance_issues": ["PageSpeed could improve.", "After-hours leads missed."],
        "growth_opps": ["24/7 AI Receptionist – capture after-hours cases", "Digital ads", "Compliance upgrades"],
        "speed_score": 62
    },
    {
        "business": "The Fernandez Firm",
        "industry": "Personal Injury Law",
        "url": "https://www.fernandezfirm.com/",
        "email": "info@fernandezfirm.com",
        "contact_name": "Frank Fernandez",  # VERIFIED from list
        "liability_issues": ["Contact forms without consent.", "High call volume."],
        "performance_issues": ["PageSpeed needs improvement.", "Lead capture limited."],
        "growth_opps": ["24/7 AI Receptionist", "SMS follow-up sequences", "Compliance pages"],
        "speed_score": 64
    },
    {
        "business": "Roman Austin Personal Injury",
        "industry": "Personal Injury Law",
        "url": "https://romanaustin.com/",
        "email": "info@romanaustin.com",
        "contact_name": "John Austin",  # VERIFIED from list
        "liability_issues": ["No visible privacy policy.", "Manual intake process."],
        "performance_issues": ["PageSpeed could be optimized.", "Mobile experience limited."],
        "growth_opps": ["24/7 AI Receptionist", "Compliance solutions", "Digital ads"],
        "speed_score": 66
    },
    {
        "business": "Florin Roebig",
        "industry": "Personal Injury Law",
        "url": "https://florinroebig.com/",
        "email": "info@florinroebig.com",
        "contact_name": "Wil Florin",  # VERIFIED from list
        "liability_issues": ["No privacy/terms visible.", "Heavy call volume."],
        "performance_issues": ["PageSpeed needs optimization.", "Competitive market."],
        "growth_opps": ["24/7 AI Receptionist", "Digital ads and newsletters", "Compliance upgrades"],
        "speed_score": 58
    }
]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        print("🚀 SENDING BATCH 5 LIVE - PERSONALIZED")
        send_batch(BATCH_5, live=True)
    else:
        print("📧 SENDING BATCH 5 PREVIEWS TO OWNER - PERSONALIZED")
        send_batch(BATCH_5, live=False)
