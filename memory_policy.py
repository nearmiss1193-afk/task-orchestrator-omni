"""
MEMORY POLICY - What to Store and What to NEVER Store
"""

# ============================================================================
# ALLOWED TO STORE (Business-Relevant)
# ============================================================================
ALLOWED_MEMORY_TYPES = {
    "identity": ["name", "company", "role", "email", "phone"],
    "intent": ["current_intent", "pipeline_stage", "lead_fit"],
    "business": ["industry", "team_size", "tech_stack", "crm_software"],
    "needs": ["pain_points", "goals", "priorities"],
    "objections": ["objection_type", "objection_detail", "response_that_worked"],
    "booking": ["booking_status", "preferred_days", "preferred_times", "booked_at"],
    "permissions": ["follow_up_permission", "opt_out", "opt_out_reason"],
    "sentiment": ["sentiment", "urgency_level"],
}

# ============================================================================
# NEVER STORE (Sensitive/PII)
# ============================================================================
FORBIDDEN_PATTERNS = [
    # Health
    "health", "medical", "diagnosis", "prescription", "hospital", "doctor",
    # Religion/Politics
    "religion", "religious", "church", "temple", "mosque", "political", "vote", "party",
    # Financial PII
    "ssn", "social security", "driver license", "drivers license", "bank account",
    "routing number", "credit card", "card number", "cvv", "expiration date",
    "payment card", "debit card",
    # Other PII
    "passport", "birth certificate",
]

def is_safe_to_store(key: str, value: str) -> bool:
    """Check if a memory item is safe to store"""
    text = f"{key} {value}".lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in text:
            return False
    return True

def filter_memory(key: str, value: str) -> tuple:
    """Filter memory - returns (is_safe, reason)"""
    if not is_safe_to_store(key, value):
        return False, "Contains forbidden sensitive data"
    return True, "OK"
