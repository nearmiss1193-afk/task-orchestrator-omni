"""
RESPONSE ROUTER - Inbound Message Classification & Routing
Empire Analytics Infrastructure

Routes inbound messages based on intent:
- BOOKING → Auto-schedule or Sarah call
- QUESTION → AI response
- INTEREST → Fast-track to Sarah
- OBJECTION → Escalate to human
- UNSUBSCRIBE → Mark DQ
"""

import os
import re
import json
import datetime
from typing import Tuple, Optional

# For Modal deployment
try:
    import modal
    from supabase import create_client, Client
    import google.generativeai as genai
    MODAL_AVAILABLE = True
except ImportError:
    MODAL_AVAILABLE = False

# ============ INTENT PATTERNS ============
INTENT_PATTERNS = {
    "booking": [
        r"book", r"schedule", r"appointment", r"meet", r"call me",
        r"when.*available", r"set up", r"demo", r"let'?s talk"
    ],
    "question": [
        r"how", r"what", r"why", r"can you", r"do you", r"is it",
        r"tell me", r"explain", r"more info", r"\?"
    ],
    "interest": [
        r"interested", r"sounds good", r"tell me more", r"curious",
        r"love to", r"want to", r"need", r"looking for"
    ],
    "objection": [
        r"too expensive", r"not now", r"busy", r"maybe later",
        r"not interested", r"already have", r"no thanks", r"cost"
    ],
    "unsubscribe": [
        r"stop", r"unsubscribe", r"remove", r"opt out", r"don'?t contact"
    ],
    "negative": [
        r"fuck", r"spam", r"scam", r"leave me alone", r"reported"
    ]
}

# ============ ROUTING CONFIG ============
ROUTING_RULES = {
    "booking": {
        "action": "auto_book",
        "priority": "high",
        "confidence_threshold": 0.7,
        "escalate": False
    },
    "interest": {
        "action": "sarah_call",
        "priority": "high", 
        "confidence_threshold": 0.6,
        "escalate": False
    },
    "question": {
        "action": "ai_response",
        "priority": "medium",
        "confidence_threshold": 0.5,
        "escalate": False
    },
    "objection": {
        "action": "escalate",
        "priority": "low",
        "confidence_threshold": 0.6,
        "escalate": True
    },
    "unsubscribe": {
        "action": "mark_dq",
        "priority": "low",
        "confidence_threshold": 0.8,
        "escalate": False
    },
    "negative": {
        "action": "mark_dq",
        "priority": "low",
        "confidence_threshold": 0.9,
        "escalate": True
    }
}

def get_supabase() -> "Client":
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    return create_client(url, key)

def get_gemini():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def classify_intent_regex(message: str) -> Tuple[str, float]:
    """Fast regex-based intent classification"""
    message_lower = message.lower()
    
    intent_scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        matches = sum(1 for p in patterns if re.search(p, message_lower))
        if matches > 0:
            intent_scores[intent] = matches / len(patterns)
    
    if not intent_scores:
        return "question", 0.3  # Default to question
    
    best_intent = max(intent_scores, key=intent_scores.get)
    return best_intent, min(intent_scores[best_intent] * 2, 1.0)

def classify_intent_ai(message: str, lead_context: dict = None) -> Tuple[str, float]:
    """Gemini-powered intent classification"""
    try:
        model = get_gemini()
        
        context = json.dumps(lead_context) if lead_context else "No context available"
        
        prompt = f"""Classify this inbound message intent. Return JSON only.

Message: "{message}"
Lead Context: {context}

Categories:
- booking: Wants to schedule/meet
- interest: Interested but not booking yet
- question: Asking for information
- objection: Has concerns/resistance
- unsubscribe: Wants to stop communication
- negative: Hostile/spam complaint

Return: {{"intent": "category", "confidence": 0.0-1.0, "reason": "brief explanation"}}"""

        response = model.generate_content(prompt)
        result = json.loads(response.text.replace('```json', '').replace('```', ''))
        return result.get("intent", "question"), result.get("confidence", 0.5)
    except Exception as e:
        # Fallback to regex
        return classify_intent_regex(message)

def get_routing_decision(intent: str, confidence: float) -> dict:
    """Determine action based on intent"""
    rules = ROUTING_RULES.get(intent, ROUTING_RULES["question"])
    
    if confidence >= rules["confidence_threshold"]:
        return {
            "action": rules["action"],
            "intent": intent,
            "confidence": confidence,
            "priority": rules["priority"],
            "escalate": rules["escalate"]
        }
    else:
        # Low confidence = escalate
        return {
            "action": "escalate",
            "intent": intent,
            "confidence": confidence,
            "priority": "medium",
            "escalate": True
        }

def route_message(message: str, contact_id: str, lead_context: dict = None, use_ai: bool = True) -> dict:
    """Main routing function"""
    # Step 1: Classify intent
    if use_ai and MODAL_AVAILABLE:
        intent, confidence = classify_intent_ai(message, lead_context)
    else:
        intent, confidence = classify_intent_regex(message)
    
    # Step 2: Get routing decision
    decision = get_routing_decision(intent, confidence)
    decision["contact_id"] = contact_id
    decision["message"] = message[:100]  # Truncate for logging
    decision["timestamp"] = datetime.datetime.now().isoformat()
    
    return decision

def execute_routing(decision: dict) -> dict:
    """Execute the routing decision"""
    action = decision["action"]
    contact_id = decision["contact_id"]
    
    if action == "auto_book":
        # Would integrate with calendar API
        return {
            "status": "booking_initiated",
            "next_step": "send_calendar_link"
        }
    
    elif action == "sarah_call":
        # Would trigger Vapi outbound call
        return {
            "status": "sarah_call_queued",
            "next_step": "vapi_outbound"
        }
    
    elif action == "ai_response":
        return {
            "status": "ai_response_pending",
            "next_step": "spartan_responder"
        }
    
    elif action == "mark_dq":
        # Update status in DB
        if MODAL_AVAILABLE:
            supabase = get_supabase()
            supabase.table("contacts_master").update({
                "status": "dq",
                "outcome": "unsubscribed"
            }).eq("ghl_contact_id", contact_id).execute()
        return {
            "status": "lead_dq",
            "next_step": "removed_from_pipeline"
        }
    
    elif action == "escalate":
        return {
            "status": "escalated",
            "next_step": "human_review_required"
        }
    
    return {"status": "unknown", "next_step": "manual_review"}

def update_outcome(contact_id: str, outcome: str):
    """Update lead outcome in database"""
    if MODAL_AVAILABLE:
        supabase = get_supabase()
        supabase.table("contacts_master").update({
            "outcome": outcome,
            "outcome_at": datetime.datetime.now().isoformat(),
            "last_response_at": datetime.datetime.now().isoformat()
        }).eq("ghl_contact_id", contact_id).execute()

# ============ CLI / TEST MODE ============
def run_test():
    """Test classification with sample messages"""
    test_messages = [
        ("Can we schedule a call tomorrow at 2pm?", "booking"),
        ("How much does this cost?", "question"),
        ("Sounds interesting, tell me more", "interest"),
        ("I'm not interested right now, maybe later", "objection"),
        ("STOP texting me, unsubscribe", "unsubscribe"),
        ("This is spam, I'm reporting you", "negative"),
        ("What exactly does your AI do?", "question"),
        ("Let's set up a demo", "booking"),
    ]
    
    print("=" * 60)
    print("RESPONSE ROUTER TEST")
    print("=" * 60)
    
    correct = 0
    for message, expected in test_messages:
        intent, confidence = classify_intent_regex(message)
        decision = get_routing_decision(intent, confidence)
        
        status = "✅" if intent == expected else "❌"
        if intent == expected:
            correct += 1
            
        print(f"\n{status} Message: \"{message[:40]}...\"")
        print(f"   Expected: {expected} | Got: {intent} ({confidence:.0%})")
        print(f"   Action: {decision['action']} | Priority: {decision['priority']}")
    
    print(f"\n{'=' * 60}")
    print(f"Accuracy: {correct}/{len(test_messages)} ({correct/len(test_messages):.0%})")

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        run_test()
    else:
        print("Usage: python response_router.py --test")
