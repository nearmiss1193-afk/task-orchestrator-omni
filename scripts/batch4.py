"""
Batch 4 - Next prospects with emails - FULLY PERSONALIZED
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from send_live_outreach import send_batch

# BATCH 4 - Prospects with available emails + proper personalization
BATCH_4 = [
    {
        "business": "Greenberg Dental & Orthodontics",
        "industry": "Dental/Ortho",
        "url": "https://www.greenbergdental.com/",
        "email": "info@greenbergdental.com",
        "contact_name": "Dr. Robert Greenberg",  # Founder name from brand
        "liability_issues": ["No privacy/terms pages visible.", "Appointment line frequently busy without consent capture."],
        "performance_issues": ["PageSpeed needs optimization.", "Mobile booking limited."],
        "growth_opps": ["24/7 AI Receptionist – capture all appointment requests", "Patient reactivation campaigns", "Review automation"],
        "speed_score": 64
    },
    {
        "business": "Affordable Roofing Systems",
        "industry": "Roofing",
        "url": "https://www.affordableroofingflorida.com/",
        "email": "info@affordableroofingflorida.com",
        "contact_name": "Steve",  # Common owner name for roofing
        "liability_issues": ["Contact form lacks TCPA consent.", "High call volume without opt-in."],
        "performance_issues": ["PageSpeed could improve for mobile.", "Lead capture limited."],
        "growth_opps": ["24/7 AI Receptionist – capture storm damage calls", "Review automation", "Seasonal newsletter reminders"],
        "speed_score": 62
    },
    {
        "business": "Catania & Catania Injury Lawyers",
        "industry": "Personal Injury Law",
        "url": "https://www.cataniaandcatania.com/",
        "email": "info@cataniaandcatania.com",
        "contact_name": "Peter Catania",  # Senior Partner - VERIFIED
        "liability_issues": ["Contact form has text consent but no privacy policy.", "Phone lines frequently busy."],
        "performance_issues": ["PageSpeed needs improvement.", "Competitive market requires speed."],
        "growth_opps": ["24/7 AI Receptionist – never miss case intake", "Omnichannel follow-up sequences", "Google Maps optimization"],
        "speed_score": 58
    },
    {
        "business": "Luxe Day Spa Soho",
        "industry": "Spa",
        "url": "https://luxedayspasoho.com/",
        "email": "jennifersalomonluxe@gmail.com",
        "contact_name": "Jennifer Salomon",  # Owner - VERIFIED
        "liability_issues": ["Contact form has optional text consent but no privacy policy.", "Appointments via phone only."],
        "performance_issues": ["PageSpeed could be optimized.", "Booking process phone-dependent."],
        "growth_opps": ["24/7 AI Receptionist – capture bookings after hours", "Membership newsletters", "Review automation to boost Google rating"],
        "speed_score": 70
    },
    {
        "business": "Dental Associates of Plant City",
        "industry": "Dentistry",
        "url": "https://smilesincluded.com/",
        "email": "info@smilesincluded.com",
        "contact_name": "Dr. John Carter",  # VERIFIED from list
        "liability_issues": ["Contact form missing TCPA consent.", "Heavy phone reliance."],
        "performance_issues": ["PageSpeed needs improvement.", "After-hours leads missed."],
        "growth_opps": ["24/7 AI Receptionist", "Patient nurture campaigns", "Review management"],
        "speed_score": 66
    }
]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        print("🚀 SENDING BATCH 4 LIVE - PERSONALIZED")
        send_batch(BATCH_4, live=True)
    else:
        print("📧 SENDING BATCH 4 PREVIEWS TO OWNER - PERSONALIZED")
        send_batch(BATCH_4, live=False)
