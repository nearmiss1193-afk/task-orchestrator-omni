"""
SARAH DISPATCHER - 4-Step Memory Protocol
For EVERY inbound call/text:
1. Retrieve memory
2. Respond (with memory context)
3. Write memory
4. Self-improve (lightweight)
"""
import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, List, Any

# Supabase config
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", 
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAfqN89E6mIoKT3OWNKKXrN4xZIqoOHHNo")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# =============================================================================
# STEP 1: RETRIEVE MEMORY
# =============================================================================

def supabase_get_contact_memory(phone_or_email: str) -> Dict:
    """
    STEP 1: Retrieve contact memory before responding.
    Returns contact profile + memories + recent interactions.
    """
    result = {
        "contact": None,
        "is_new": True,
        "memories": [],
        "recent_interactions": [],
        "context_string": ""
    }
    
    # Try to find contact by phone first, then email
    contact = None
    
    if phone_or_email.startswith("+") or phone_or_email[0].isdigit():
        # It's a phone number
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/contacts",
            headers=HEADERS,
            params={"phone": f"eq.{phone_or_email}", "limit": 1}
        )
        if r.status_code == 200 and r.json():
            contact = r.json()[0]
    else:
        # It's an email
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/contacts",
            headers=HEADERS,
            params={"email": f"eq.{phone_or_email}", "limit": 1}
        )
        if r.status_code == 200 and r.json():
            contact = r.json()[0]
    
    if contact:
        result["contact"] = contact
        result["is_new"] = False
        contact_id = contact.get("id")
        
        # Get memories (high confidence only)
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/memories",
            headers=HEADERS,
            params={
                "contact_id": f"eq.{contact_id}",
                "confidence": "gte.0.7",
                "order": "priority.asc",
                "limit": 10
            }
        )
        if r.status_code == 200:
            result["memories"] = r.json()
        
        # Get last 3 interactions
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/interactions",
            headers=HEADERS,
            params={
                "contact_id": f"eq.{contact_id}",
                "order": "created_at.desc",
                "limit": 3
            }
        )
        if r.status_code == 200:
            result["recent_interactions"] = r.json()
        
        # Build context string for AI
        result["context_string"] = _build_context_string(contact, result["memories"], result["recent_interactions"])
    
    return result


def _build_context_string(contact: Dict, memories: List, interactions: List) -> str:
    """Build formatted context string for AI prompt injection"""
    lines = ["[CONTACT_PROFILE]"]
    lines.append(f"Name: {contact.get('name', 'Unknown')}")
    lines.append(f"Phone: {contact.get('phone', 'Unknown')}")
    lines.append(f"Email: {contact.get('email', 'Unknown')}")
    lines.append(f"Stage: {contact.get('pipeline_stage', 'new')}")
    lines.append(f"Sentiment: {contact.get('sentiment', 'Unknown')}")
    
    lines.append("\n[KEY_MEMORY - HIGH CONFIDENCE]")
    if memories:
        for m in memories:
            lines.append(f"- {m.get('memory_type', 'fact')}: {m.get('key')} = {m.get('value')} (conf: {m.get('confidence', 1.0)})")
    else:
        lines.append("- No prior memory")
    
    lines.append("\n[RECENT_INTERACTIONS - LAST 3]")
    if interactions:
        for i in interactions:
            date = i.get("created_at", "")[:10]
            lines.append(f"- {date} | {i.get('channel', 'unknown')} | {i.get('intent', 'unknown')} | {i.get('outcome', 'unknown')}")
    else:
        lines.append("- No prior interactions")
    
    return "\n".join(lines)


# =============================================================================
# STEP 3: WRITE MEMORY
# =============================================================================

def supabase_upsert_interaction(
    phone: str,
    channel: str,  # 'sms' or 'call'
    direction: str,  # 'inbound' or 'outbound'
    user_message: str,
    ai_response: str,
    intent: str = None,
    outcome: str = None,
    sentiment: str = None,
    escalated: bool = False,
    escalation_reason: str = None
) -> Dict:
    """
    STEP 3a: Save interaction to database.
    """
    # Get or create contact
    contact_id = _get_or_create_contact_id(phone)
    
    interaction = {
        "contact_id": contact_id,
        "phone": phone,
        "channel": channel,
        "direction": direction,
        "user_message": user_message,
        "ai_response": ai_response,
        "intent": intent,
        "outcome": outcome,
        "sentiment": sentiment,
        "escalated": escalated,
        "escalation_reason": escalation_reason
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/interactions",
        headers={**HEADERS, "Prefer": "return=representation"},
        json=interaction
    )
    
    if r.status_code in [200, 201]:
        result = r.json()
        return result[0] if isinstance(result, list) else result
    return {"error": r.text}


def supabase_upsert_memory(
    phone: str,
    memory_type: str,  # 'fact', 'preference', 'objection', 'constraint', 'trait'
    key: str,
    value: str,
    confidence: float = 0.8
) -> bool:
    """
    STEP 3b: Save memory item to database.
    Only stores business-relevant facts with confidence scores.
    """
    # Get contact ID
    contact_id = _get_or_create_contact_id(phone)
    
    # Check if memory already exists (update if so)
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/memories",
        headers=HEADERS,
        params={
            "contact_id": f"eq.{contact_id}",
            "key": f"eq.{key}",
            "limit": 1
        }
    )
    
    if r.status_code == 200 and r.json():
        # Update existing memory
        existing_id = r.json()[0]["id"]
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/memories?id=eq.{existing_id}",
            headers=HEADERS,
            json={"value": value, "confidence": confidence}
        )
        return r.status_code in [200, 204]
    else:
        # Insert new memory
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/memories",
            headers=HEADERS,
            json={
                "contact_id": contact_id,
                "phone": phone,
                "memory_type": memory_type,
                "key": key,
                "value": value,
                "confidence": confidence
            }
        )
        return r.status_code in [200, 201]


def _get_or_create_contact_id(phone: str) -> Optional[str]:
    """Get existing contact ID or create new contact"""
    # Try to find existing
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/contacts",
        headers=HEADERS,
        params={"phone": f"eq.{phone}", "limit": 1}
    )
    
    if r.status_code == 200 and r.json():
        return r.json()[0]["id"]
    
    # Create new contact
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/contacts",
        headers={**HEADERS, "Prefer": "return=representation"},
        json={
            "phone": phone,
            "pipeline_stage": "new"
        }
    )
    
    if r.status_code in [200, 201]:
        result = r.json()
        return result[0]["id"] if isinstance(result, list) else result.get("id")
    return None


# =============================================================================
# STEP 4: SELF-IMPROVE (Lightweight)
# =============================================================================

def log_objection(phone: str, objection_type: str, detail: str):
    """
    STEP 4a: Log objection that caused failure to book.
    Types: price, bot, trust, timing, other
    """
    return supabase_upsert_memory(
        phone=phone,
        memory_type="objection",
        key=objection_type,
        value=detail,
        confidence=0.9
    )


def log_kb_gap(question: str, context: str = None):
    """
    STEP 4b: Log question that couldn't be answered.
    Stored in playbook_updates for human review.
    """
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/playbook_updates",
        headers=HEADERS,
        json={
            "update_type": "kb_gap",
            "change_description": question,
            "reason": context or "User asked question Sarah couldn't answer",
            "status": "proposed"
        }
    )
    return r.status_code in [200, 201]


# =============================================================================
# FULL DISPATCHER FLOW
# =============================================================================

SARAH_SYSTEM_PROMPT = """You are "Sarah," the professional dispatcher for AI Service Co.

HARD RULES:
- Never ask for or take credit card info over voice/SMS.
- For life-threatening emergencies (gas leak, fire, CO alarm), instruct them to hang up and dial 911.
- No legal/insurance advice. You may collect claim details but never advise.

BOOKING:
- Default appointment: "Sovereign Strategy Session" (15 min audit + AI demo).
- Booking link: https://link.aiserviceco.com/discovery
- Suggest times in the next 48 hours.

OUTPUT STYLE:
- SMS: 1-2 short sentences, include booking link early.
- Call: calm, concise, confirm details, then book.

You have access to the contact's memory below. Use it to personalize your response and avoid repeating questions.
"""


def handle_inbound(phone: str, channel: str, message: str) -> Dict:
    """
    Full 4-step dispatcher flow for inbound call/text.
    Returns AI response and memory updates.
    """
    # STEP 1: Retrieve memory
    memory = supabase_get_contact_memory(phone)
    
    # STEP 2: Generate response with memory context
    prompt = f"{SARAH_SYSTEM_PROMPT}\n\n{memory['context_string']}\n\n[CURRENT MESSAGE]\nChannel: {channel}\nUser: {message}"
    
    ai_response = _call_gemini(prompt)
    
    # STEP 3: Write memory
    # Determine intent and outcome from response
    intent = _classify_intent(message)
    outcome = _determine_outcome(ai_response)
    sentiment = _classify_sentiment(message)
    
    interaction = supabase_upsert_interaction(
        phone=phone,
        channel=channel,
        direction="inbound",
        user_message=message,
        ai_response=ai_response,
        intent=intent,
        outcome=outcome,
        sentiment=sentiment
    )
    
    # Extract and store memories from conversation
    extracted = _extract_memories(message, ai_response)
    for mem in extracted:
        supabase_upsert_memory(
            phone=phone,
            memory_type=mem["type"],
            key=mem["key"],
            value=mem["value"],
            confidence=mem.get("confidence", 0.8)
        )
    
    # STEP 4: Self-improve (lightweight)
    if outcome == "no_book" and "price" in message.lower():
        log_objection(phone, "price", message)
    elif outcome == "no_book" and ("bot" in message.lower() or "ai" in message.lower()):
        log_objection(phone, "bot", message)
    
    return {
        "response": ai_response,
        "is_new_contact": memory["is_new"],
        "intent": intent,
        "outcome": outcome,
        "interaction_id": interaction.get("id")
    }


def _call_gemini(prompt: str) -> str:
    """Call Gemini API for response"""
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30
        )
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"Gemini error: {e}")
    return "Hi! I'm having a brief technical issue. Can you try again in a moment? Or call us directly at (863) 337-3705."


def _classify_intent(message: str) -> str:
    """Quick intent classification"""
    msg = message.lower()
    if any(w in msg for w in ["price", "cost", "how much", "rate", "fee"]):
        return "pricing"
    elif any(w in msg for w in ["book", "schedule", "appointment", "meet", "call"]):
        return "book"
    elif any(w in msg for w in ["help", "support", "issue", "problem", "broken"]):
        return "support"
    elif any(w in msg for w in ["complaint", "refund", "cancel", "unhappy"]):
        return "complaint"
    return "other"


def _determine_outcome(response: str) -> str:
    """Determine outcome from AI response"""
    resp = response.lower()
    if "link.aiserviceco.com" in resp or "book" in resp or "schedule" in resp:
        return "send_link"
    elif "follow" in resp or "call you back" in resp:
        return "follow_up"
    elif "escalate" in resp or "manager" in resp:
        return "escalate"
    return "continue"


def _classify_sentiment(message: str) -> str:
    """Quick sentiment classification"""
    msg = message.lower()
    if any(w in msg for w in ["urgent", "asap", "emergency", "now", "immediately"]):
        return "urgent"
    elif any(w in msg for w in ["angry", "frustrated", "terrible", "awful", "worst"]):
        return "frustrated"
    return "calm"


def _extract_memories(user_message: str, ai_response: str) -> List[Dict]:
    """Extract key memories from conversation"""
    memories = []
    msg = user_message.lower()
    
    # Extract business/industry mentions
    industries = ["hvac", "plumbing", "electrical", "roofing", "landscaping", "cleaning"]
    for ind in industries:
        if ind in msg:
            memories.append({"type": "fact", "key": "industry", "value": ind, "confidence": 0.9})
    
    # Extract location mentions
    if "in " in msg:
        # Simple location extraction
        import re
        match = re.search(r'in ([A-Z][a-z]+ ?[A-Z]?[a-z]*)', user_message)
        if match:
            memories.append({"type": "fact", "key": "location", "value": match.group(1), "confidence": 0.7})
    
    # Extract preferences
    if "prefer" in msg or "like" in msg:
        memories.append({"type": "preference", "key": "stated_preference", "value": user_message[:100], "confidence": 0.8})
    
    return memories


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SARAH DISPATCHER - TEST")
    print("=" * 60)
    
    # Test with sample inbound
    result = handle_inbound(
        phone="+1234567890",
        channel="sms",
        message="Hi, I'm interested in your HVAC AI service. How much does it cost?"
    )
    
    print(f"\n[RESPONSE]")
    print(result["response"])
    print(f"\n[INTENT]: {result['intent']}")
    print(f"[OUTCOME]: {result['outcome']}")
    print(f"[NEW CONTACT]: {result['is_new_contact']}")
