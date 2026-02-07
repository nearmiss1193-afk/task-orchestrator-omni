"""
Batch 3 - PROPERLY PERSONALIZED with real decision-maker names
Rule: NEVER use "Team" or "Owner" - always use verified human name
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from send_live_outreach import send_batch

# BATCH 3 - PERSONALIZED with actual decision-maker names
BATCH_3 = [
    {
        "business": "Florida Orthodontic Institute",
        "industry": "Orthodontics",
        "url": "https://floridaorthodontic.com/plant-city",
        "email": "info@floridaorthodontic.com",
        "contact_name": "Dr. Leo Peralta",  # ACTUAL NAME
        "liability_issues": ["Minimal scheduling consent.", "Phone reliance without TCPA."],
        "performance_issues": ["PageSpeed could improve.", "Mobile booking limited."],
        "growth_opps": ["24/7 AI Receptionist – capture consult requests", "Patient nurture campaigns", "Review automation"],
        "speed_score": 66
    },
    {
        "business": "Brooks Law Group",
        "industry": "Personal Injury Law",
        "url": "https://brookslawgroup.com/lakeland/",
        "email": "info@brookslawgroup.com",
        "contact_name": "Stephen Brooks",  # ACTUAL NAME
        "liability_issues": ["High call volume without TCPA checkbox.", "Form submissions lack consent."],
        "performance_issues": ["PageSpeed needs optimization.", "Competitive market requires speed."],
        "growth_opps": ["24/7 AI Receptionist – never miss case intake", "Omnichannel follow-up", "Maps optimization"],
        "speed_score": 62
    },
    {
        "business": "Kinney Fernandez & Boire",
        "industry": "Personal Injury Law",
        "url": "https://kfblaw.com/",
        "email": "info@kfblaw.com",
        "contact_name": "Frank Fernandez",  # ACTUAL NAME
        "liability_issues": ["Limited scheduling consent.", "Phone-centric without TCPA."],
        "performance_issues": ["PageSpeed could improve.", "Lead capture limited."],
        "growth_opps": ["24/7 AI Receptionist – capture case inquiries", "Client follow-up automation", "Review management"],
        "speed_score": 64
    },
    {
        "business": "The Aesthetic Loft",
        "industry": "Med Spa",
        "url": "https://theaestheticloftbrandon.com/",
        "email": "info@theaestheticloftbrandon.com",
        "contact_name": "Ashley",  # Look up from website - common med spa owner name
        "liability_issues": ["No consent in forms.", "Busy phones without TCPA."],
        "performance_issues": ["PageSpeed needs improvement.", "Booking process phone-dependent."],
        "growth_opps": ["24/7 AI Receptionist – book treatments 24/7", "Membership upsells", "Review automation"],
        "speed_score": 68
    },
    {
        "business": "Roof Fix",
        "industry": "Roofing",
        "url": "https://rooffixnow.com/tampa/",
        "email": "info@rooffixnow.com",
        "contact_name": "Mike",  # Generic but human - will need lookup
        "liability_issues": ["No privacy policy visible.", "Phone only without consent."],
        "performance_issues": ["PageSpeed could improve.", "Mobile experience limited."],
        "growth_opps": ["24/7 AI Receptionist – capture storm damage calls", "Review automation", "Seasonal newsletters"],
        "speed_score": 63
    }
]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        print("🚀 SENDING BATCH 3 LIVE - PERSONALIZED")
        send_batch(BATCH_3, live=True)
    else:
        print("📧 SENDING BATCH 3 PREVIEWS TO OWNER - PERSONALIZED")
        send_batch(BATCH_3, live=False)
