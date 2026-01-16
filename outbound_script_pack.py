"""
OUTBOUND SCRIPT PACK - Sales Dialogue & SMS Templates
Structured, scalable, high-conversion scripts for outbound sales
"""

BOOKING_LINK = "https://link.aiserviceco.com/discovery"

# Script scenarios
SCRIPT_PACK = {
    "warm_initial": {
        "scenario": "warm_initial",
        "voice_opening": "Hi {name}, this is Christina with AI Service Co. We help service teams fix missed calls and book more jobs using autonomous AI. I noticed you had expressed interest — can I ask a quick couple questions?",
        "voice_questions": [
            "What's the biggest issue you're facing with calls or follow-up?",
            "How many techs do you have on your team?",
            "Do you use a CRM currently?"
        ],
        "voice_objection_branches": {
            "price": "I know budget is important — most teams recoup the session cost quickly from booked jobs. Our 15-min audit is tailored to your setup — can we lock that in?",
            "bot": "I'm not a simple chatbot — I'm trained on real service interactions and tailored to your business's needs. Let's walk through what that looks like.",
            "timing": "I hear you — 15 minutes now can uncover revenue opportunities you might be missing already. What slot works best?",
            "authority": "Absolutely — let me include your decision maker on the call. When works best for both of you?",
            "other": "Great question — let's cover that during the session. What time works for a quick look?"
        },
        "voice_closing_lines": [
            "Would you prefer {time_a} or {time_b} for the session?",
            "I can send a calendar link right now — when's good?"
        ],
        "sms_opening": f"Hi {{name}}, Christina from AI Service Co — we help teams convert missed calls into booked jobs. Quick 15-min audit/demo: {BOOKING_LINK}",
        "sms_followups": [
            f"Just checking back — this session usually reveals quick wins. Book here: {BOOKING_LINK}",
            f"Still curious? This demo is tailored to your business — {BOOKING_LINK}"
        ],
        "sms_closing_cta": f"Book your session here: {BOOKING_LINK}"
    },
    
    "no_answer_follow_up": {
        "scenario": "no_answer_follow_up",
        "voice_opening": "Hi {name}, this is Christina with AI Service Co. I tried reaching you about helping with your missed calls and lead follow-up. When is a good time to connect?",
        "voice_questions": [],
        "voice_objection_branches": {
            "price": f"Price comes up often — let's cover value in a quick session. Schedule here: {BOOKING_LINK}",
            "bot": f"I'm actually a conversion specialist, not a basic bot — here's a session link: {BOOKING_LINK}",
            "timing": "No problem — when's a better time for a quick 15-min session?",
            "authority": "Sure — want to loop in someone else? What works?",
            "other": f"Happy to answer any questions — session link: {BOOKING_LINK}"
        },
        "voice_closing_lines": [
            "Looking forward to speaking — what time suits you?",
            "Let's lock a slot — morning or afternoon?"
        ],
        "sms_opening": f"Missed you earlier, {{name}}. Let's find a time that works: {BOOKING_LINK}",
        "sms_followups": [
            f"Here's the booking link again: {BOOKING_LINK}",
            f"Still open to a quick look? {BOOKING_LINK}"
        ],
        "sms_closing_cta": f"Schedule your 15-min session: {BOOKING_LINK}"
    },
    
    "price_objection": {
        "scenario": "price_objection",
        "voice_opening": "I hear you — price matters. Most service teams recoup the session cost within weeks from booked jobs. This 15-min session is tailored and risk-managed. What slot works for you?",
        "voice_questions": [],
        "voice_objection_branches": {
            "price": "If pricing is still a concern, we can explore the ROI side during the session — here's a link to lock a time.",
            "bot": "I'm trained for real service interactions — here's the session link.",
            "timing": f"Scheduling now helps you get insights sooner — booking link: {BOOKING_LINK}",
            "authority": "Let's include anyone else needed — when works for all?",
            "other": "Great question — address it in the session. Here's the link."
        },
        "voice_closing_lines": [
            "Can we lock {time_a} or {time_b}?",
            "I can send a confirmation link — what's best?"
        ],
        "sms_opening": f"Price concern? This session is tailored to your needs and most see ROI fast: {BOOKING_LINK}",
        "sms_followups": [
            f"Quick reminder — book here: {BOOKING_LINK}",
            f"Got a sec? Secure a time: {BOOKING_LINK}"
        ],
        "sms_closing_cta": f"Book here: {BOOKING_LINK}"
    },
    
    "timing_objection": {
        "scenario": "timing_objection",
        "voice_opening": "I completely understand. 15 minutes is all we need to show you what you're missing. When would be a better time this week?",
        "voice_questions": [],
        "voice_objection_branches": {
            "price": "We can cover pricing on the call — most teams see quick ROI.",
            "bot": "I'm a trained conversion specialist, not a basic bot.",
            "timing": "What time this week works better for you?",
            "authority": "Should I include your business partner?",
            "other": "Let's address that in the session."
        },
        "voice_closing_lines": [
            "Morning or afternoon work better?",
            "How about later this week?"
        ],
        "sms_opening": f"Busy now? No problem. Lock a 15-min slot when it fits: {BOOKING_LINK}",
        "sms_followups": [
            f"When's good? {BOOKING_LINK}",
            f"Quick slot this week? {BOOKING_LINK}"
        ],
        "sms_closing_cta": f"Schedule: {BOOKING_LINK}"
    },
    
    "touch_1": {
        "scenario": "touch_1",
        "voice_opening": "Hi {name}, this is Christina with AI Service Co. I just reviewed {company}'s marketing and found some quick wins you might be missing. Do you have 2 minutes?",
        "voice_questions": [
            "Are you currently missing calls or struggling with follow-up?",
            "How many techs on your team?"
        ],
        "voice_objection_branches": {
            "price": "Value shows up fast — let's lock a 15-min session.",
            "bot": "I'm a trained sales specialist, not a basic chatbot.",
            "timing": "Just 15 minutes — morning or afternoon?",
            "authority": "Let's include your decision maker.",
            "other": "Great question — let's cover it in the session."
        },
        "voice_closing_lines": [
            "Would {time_a} or {time_b} work?",
            "I'll send the calendar link now."
        ],
        "sms_opening": f"Hi {{name}}, Christina from AI Service Co. Your marketing audit for {{company}} is ready — quick 15-min walkthrough? {BOOKING_LINK}",
        "sms_followups": [],
        "sms_closing_cta": f"Book: {BOOKING_LINK}"
    },
    
    "touch_2": {
        "scenario": "touch_2",
        "voice_opening": "Hi {name}, following up on my earlier call. I found 3 specific things that could help {company} get more leads this month. Got 15 minutes?",
        "voice_questions": [],
        "voice_objection_branches": {
            "price": "Most teams see ROI in weeks.",
            "bot": "Real AI, real results.",
            "timing": "15 min is all we need.",
            "authority": "Include your partner — when works?",
            "other": "Let's address it in the session."
        },
        "voice_closing_lines": [
            "What time works today or tomorrow?"
        ],
        "sms_opening": f"Quick follow-up on {{company}} — I found 3 things that could help you get more leads. Got 15 min? {BOOKING_LINK}",
        "sms_followups": [],
        "sms_closing_cta": f"Grab a slot: {BOOKING_LINK}"
    },
    
    "touch_3": {
        "scenario": "touch_3",
        "voice_opening": "Hi {name}, last call about {company}'s audit. I'm moving on to other businesses tomorrow — if you want the free strategy session, now's the time.",
        "voice_questions": [],
        "voice_objection_branches": {
            "price": "Last chance — ROI is fast for most teams.",
            "bot": "Real AI specialist here.",
            "timing": "This is my final outreach.",
            "authority": "Happy to include anyone else.",
            "other": "Let's cover it now."
        },
        "voice_closing_lines": [
            "Last chance — morning or afternoon?"
        ],
        "sms_opening": f"Last chance, {{name}} — your {{company}} audit expires soon. Book now: {BOOKING_LINK}",
        "sms_followups": [],
        "sms_closing_cta": f"Final call: {BOOKING_LINK}"
    }
}


def get_script(scenario: str, channel: str = "sms") -> dict:
    """
    Get script for a scenario
    
    Args:
        scenario: One of warm_initial, no_answer_follow_up, price_objection, touch_1, touch_2, touch_3
        channel: 'voice' or 'sms'
    
    Returns:
        Dict with appropriate script fields
    """
    script = SCRIPT_PACK.get(scenario, SCRIPT_PACK["warm_initial"])
    
    if channel == "voice":
        return {
            "opening": script["voice_opening"],
            "questions": script["voice_questions"],
            "objection_branches": script["voice_objection_branches"],
            "closing_lines": script["voice_closing_lines"]
        }
    else:
        return {
            "opening": script["sms_opening"],
            "followups": script["sms_followups"],
            "closing_cta": script["sms_closing_cta"]
        }


def format_script(template: str, **kwargs) -> str:
    """
    Format script template with actual values
    
    Args:
        template: Script template with {placeholders}
        **kwargs: Values to fill in (name, company, time_a, time_b, etc.)
    
    Returns:
        Formatted script string
    """
    try:
        return template.format(**kwargs)
    except KeyError:
        # Return template with unfilled placeholders if values missing
        return template


# Export
__all__ = ["SCRIPT_PACK", "get_script", "format_script", "BOOKING_LINK"]
