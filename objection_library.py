"""
SHARED OBJECTION & RESPONSE LIBRARY
Centralized objection handling for Sarah (inbound) and Christina (outbound)
"""

# Locked constants
LOCKED_CONSTANTS = {
    "pricing": {
        "starter": 297,
        "lite": 497,
        "growth": 997,
        "enterprise": "custom"
    },
    "booking": {
        "session_name": "Sovereign Strategy Session",
        "duration": "15 min",
        "link": "https://link.aiserviceco.com/discovery"
    },
    "compliance": {
        "no_payment_sms_voice": True,
        "stop_means_optout": True,
        "emergency_911": True
    }
}

BOOKING_LINK = "https://link.aiserviceco.com/discovery"

# Objection library
OBJECTION_LIBRARY = {
    "price": {
        "objection_category": "price",
        "best_response_voice": "Our Sovereign Strategy Session is structured to deliver immediate insights on missed calls, follow-ups, and revenue gaps. Pricing is tiered ($297–$997) based on scope, and most teams recoup value quickly from booked jobs. Let's set up a 15-minute slot so you can see that for yourself.",
        "best_response_sms": f"Our session cost is $297–$997 depending on your needs. Most teams recover that value quickly — book a quick demo: {BOOKING_LINK}",
        "closing_cta_voice": "Does {time_a} or {time_b} work for your 15-min session?",
        "closing_cta_sms": f"Tap to schedule: {BOOKING_LINK}",
        "variants": [
            {"type": "short", "voice": "Pricing starts at $297/mo — most teams see ROI in weeks.", "sms": f"$297/mo to start. Book demo: {BOOKING_LINK}"},
            {"type": "long", "voice": "I understand price matters. Our tiered pricing ($297-$997) is designed to match your team size and needs. The 15-min session shows exact ROI potential.", "sms": f"Pricing is $297-$997 based on scope. Quick 15-min demo shows ROI: {BOOKING_LINK}"},
            {"type": "alternative", "voice": "What if I showed you how this pays for itself? Quick 15 minutes.", "sms": f"Most teams recoup cost fast. See how: {BOOKING_LINK}"}
        ]
    },
    
    "bot": {
        "objection_category": "bot",
        "best_response_voice": "I understand the question. I'm not a static chatbot — I'm trained on real service interactions and tailored to your business. I handle real qualifications and booking tasks. Can I book a quick 15-min session so you see how it works live?",
        "best_response_sms": f"I'm not a basic chatbot — I qualify leads and book sessions with real business logic. Book a demo: {BOOKING_LINK}",
        "closing_cta_voice": "Would you like me to schedule that now?",
        "closing_cta_sms": f"Schedule here: {BOOKING_LINK}",
        "variants": [
            {"type": "short", "voice": "I'm an AI assistant that handles real business tasks. Want to see it live?", "sms": f"Real AI, real results. Demo: {BOOKING_LINK}"},
            {"type": "long", "voice": "Great question. I'm built on advanced AI that learns from your industry and business context. I qualify leads, handle objections, and book appointments — all autonomously.", "sms": f"Advanced AI trained on service businesses. See it work: {BOOKING_LINK}"}
        ]
    },
    
    "timing": {
        "objection_category": "timing",
        "best_response_voice": "I get timing is important. That's why this session is just 15 minutes — enough to uncover your biggest gaps without wasting your day. What time today or tomorrow works best?",
        "best_response_sms": f"Timing is key — our 15-min demo fits your schedule & reveals quick wins. Book: {BOOKING_LINK}",
        "closing_cta_voice": "How about {specific_option}?",
        "closing_cta_sms": f"Grab a slot: {BOOKING_LINK}",
        "variants": [
            {"type": "short", "voice": "Just 15 minutes. Morning or afternoon?", "sms": f"15 min slot? {BOOKING_LINK}"},
            {"type": "alternative", "voice": "What if we found a 15-min window this week?", "sms": f"Quick 15-min slot: {BOOKING_LINK}"}
        ]
    },
    
    "authority": {
        "objection_category": "authority",
        "best_response_voice": "Great question — absolutely. Let's include your decision-maker so everyone's aligned. What times are good for both of you?",
        "best_response_sms": f"Want to include your decision maker? Schedule a time that works for all: {BOOKING_LINK}",
        "closing_cta_voice": "What time works for you both?",
        "closing_cta_sms": f"Choose a time: {BOOKING_LINK}",
        "variants": [
            {"type": "short", "voice": "Include your partner — what time works for all?", "sms": f"Bring your team: {BOOKING_LINK}"},
            {"type": "alternative", "voice": "Happy to have everyone on the call. When's good?", "sms": f"Include decision makers: {BOOKING_LINK}"}
        ]
    },
    
    "current_solution": {
        "objection_category": "current_solution",
        "best_response_voice": "Totally makes sense — many teams use existing tools. This session shows how our autonomous AI layers on top of your current systems to reduce missed calls & increase bookings. Let's find 15 minutes to look at it.",
        "best_response_sms": f"We integrate with current systems and drive results on top — book a quick look: {BOOKING_LINK}",
        "closing_cta_voice": "When can we set your session?",
        "closing_cta_sms": f"Book here: {BOOKING_LINK}",
        "variants": [
            {"type": "short", "voice": "We work alongside your current tools. Quick demo?", "sms": f"Works with your tools: {BOOKING_LINK}"},
            {"type": "alternative", "voice": "What results are you seeing now? I can show how we improve on that.", "sms": f"See how we boost your current setup: {BOOKING_LINK}"}
        ]
    },
    
    "unknown": {
        "objection_category": "unknown",
        "best_response_voice": "Could you clarify what you mean?",
        "best_response_sms": "Can you clarify what you're asking?",
        "closing_cta_voice": "",
        "closing_cta_sms": "",
        "variants": []
    }
}


def get_objection_response(category: str, channel: str = "sms") -> dict:
    """
    Get the appropriate response for an objection category
    
    Args:
        category: One of price, bot, timing, authority, current_solution, unknown
        channel: 'voice' or 'sms'
    
    Returns:
        Dict with response text and closing CTA
    """
    objection = OBJECTION_LIBRARY.get(category, OBJECTION_LIBRARY["unknown"])
    
    if channel == "voice":
        return {
            "response": objection["best_response_voice"],
            "closing_cta": objection["closing_cta_voice"],
            "variants": [v for v in objection.get("variants", []) if v.get("voice")]
        }
    else:
        return {
            "response": objection["best_response_sms"],
            "closing_cta": objection["closing_cta_sms"],
            "variants": [v for v in objection.get("variants", []) if v.get("sms")]
        }


def detect_objection(message: str) -> str:
    """
    Detect objection category from message text
    
    Returns: category string
    """
    message_lower = message.lower()
    
    # Price objections
    if any(word in message_lower for word in ["price", "cost", "expensive", "afford", "budget", "how much", "pricing"]):
        return "price"
    
    # Bot/AI objections
    if any(word in message_lower for word in ["bot", "real person", "human", "ai", "robot", "automated"]):
        return "bot"
    
    # Timing objections
    if any(word in message_lower for word in ["busy", "time", "later", "not now", "maybe", "think about"]):
        return "timing"
    
    # Authority objections
    if any(word in message_lower for word in ["boss", "partner", "decision", "owner", "manager", "check with"]):
        return "authority"
    
    # Current solution objections
    if any(word in message_lower for word in ["already have", "using", "current", "existing", "competitor"]):
        return "current_solution"
    
    return "unknown"


# Export for other modules
__all__ = [
    "OBJECTION_LIBRARY",
    "LOCKED_CONSTANTS",
    "BOOKING_LINK",
    "get_objection_response",
    "detect_objection"
]
