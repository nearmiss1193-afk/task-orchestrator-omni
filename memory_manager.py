"""
MEMORY MANAGER - The ONLY agent with write authority to canonical memory
All other agents must submit suggestions that this manager validates.
"""
import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo")
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# FORBIDDEN - Never store these
FORBIDDEN_PATTERNS = [
    "ssn", "social security", "driver license", "bank account",
    "credit card", "card number", "cvv", "routing number", "passport",
    "health", "medical", "diagnosis", "religion", "religious", "political"
]

# MINIMUM CONFIDENCE to commit
MIN_CONFIDENCE = 0.7


def is_safe_to_store(value: str) -> bool:
    """Check if memory is safe to store (no PII/sensitive data)"""
    text = value.lower()
    return not any(p in text for p in FORBIDDEN_PATTERNS)


def validate_suggestion(suggestion: Dict) -> tuple:
    """
    Validate a memory suggestion from a specialist agent.
    Returns (is_valid, reason)
    """
    key = suggestion.get("key", "")
    value = suggestion.get("value", "")
    confidence = suggestion.get("confidence", 0.5)
    
    # Check confidence threshold
    if confidence < MIN_CONFIDENCE:
        return False, f"Confidence {confidence} below threshold {MIN_CONFIDENCE}"
    
    # Check for forbidden patterns
    if not is_safe_to_store(f"{key} {value}"):
        return False, "Contains forbidden sensitive data"
    
    # Check for empty values
    if not key or not value:
        return False, "Missing key or value"
    
    return True, "OK"


def commit_memory(phone: str, suggestion: Dict) -> bool:
    """
    Commit a validated memory suggestion to the canonical memories table.
    Only the Memory Manager should call this.
    """
    is_valid, reason = validate_suggestion(suggestion)
    if not is_valid:
        log_rejection(phone, suggestion, reason)
        return False
    
    # Get or create contact
    contact_id = get_contact_id(phone)
    
    # Check for existing memory with same key
    existing = get_existing_memory(contact_id, suggestion["key"])
    
    if existing:
        # Update if new confidence is higher
        if suggestion.get("confidence", 0.8) >= existing.get("confidence", 0.5):
            r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/memories?id=eq.{existing['id']}",
                headers=HEADERS,
                json={
                    "value": suggestion["value"],
                    "confidence": suggestion.get("confidence", 0.8)
                }
            )
            log_event("memory_updated", phone, True, key=suggestion["key"])
            return r.status_code in [200, 204]
        else:
            return False  # Existing memory has higher confidence
    else:
        # Insert new memory
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/memories",
            headers=HEADERS,
            json={
                "contact_id": contact_id,
                "phone": phone,
                "memory_type": suggestion.get("type", "fact"),
                "key": suggestion["key"],
                "value": suggestion["value"],
                "confidence": suggestion.get("confidence", 0.8)
            }
        )
        log_event("memory_created", phone, True, key=suggestion["key"])
        return r.status_code in [200, 201]


def process_suggestions(phone: str, suggestions: List[Dict]) -> Dict:
    """
    Process a batch of memory suggestions from specialist agents.
    Validates each and commits valid ones.
    """
    results = {"accepted": 0, "rejected": 0, "errors": []}
    
    for suggestion in suggestions:
        try:
            if commit_memory(phone, suggestion):
                results["accepted"] += 1
            else:
                results["rejected"] += 1
        except Exception as e:
            results["errors"].append(str(e))
    
    return results


def get_contact_id(phone: str) -> Optional[str]:
    """Get existing contact ID or create new contact"""
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
        json={"phone": phone, "pipeline_stage": "new"}
    )
    
    if r.status_code in [200, 201]:
        result = r.json()
        return result[0]["id"] if isinstance(result, list) else result.get("id")
    return None


def get_existing_memory(contact_id: str, key: str) -> Optional[Dict]:
    """Check if memory with this key exists for contact"""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/memories",
        headers=HEADERS,
        params={"contact_id": f"eq.{contact_id}", "key": f"eq.{key}", "limit": 1}
    )
    if r.status_code == 200 and r.json():
        return r.json()[0]
    return None


def log_rejection(phone: str, suggestion: Dict, reason: str):
    """Log rejected memory suggestion"""
    requests.post(
        f"{SUPABASE_URL}/rest/v1/event_log",
        headers=HEADERS,
        json={
            "event_type": "memory_rejected",
            "phone": phone,
            "success": False,
            "error_message": reason,
            "context": {"key": suggestion.get("key"), "value": suggestion.get("value", "")[:100]}
        }
    )


def log_event(event_type: str, phone: str, success: bool, **kwargs):
    """Log memory manager event"""
    requests.post(
        f"{SUPABASE_URL}/rest/v1/event_log",
        headers=HEADERS,
        json={
            "event_type": event_type,
            "phone": phone,
            "success": success,
            "context": kwargs
        }
    )


def handle_opt_out(phone: str) -> bool:
    """Process opt-out request - delete all memories for this contact"""
    # Update contact
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/contacts?phone=eq.{phone}",
        headers=HEADERS,
        json={"opt_out": True, "pipeline_stage": "opted_out"}
    )
    
    # Delete memories (or mark as deleted)
    r2 = requests.delete(
        f"{SUPABASE_URL}/rest/v1/memories?phone=eq.{phone}",
        headers=HEADERS
    )
    
    log_event("opt_out_processed", phone, True)
    return r.status_code in [200, 204]


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MEMORY MANAGER - TEST")
    print("=" * 60)
    
    # Test suggestions
    test_suggestions = [
        {"key": "industry", "value": "HVAC", "confidence": 0.9, "type": "fact"},
        {"key": "team_size", "value": "5-10 employees", "confidence": 0.8, "type": "fact"},
        {"key": "credit_card", "value": "4111-xxxx-xxxx", "confidence": 0.9, "type": "fact"},  # Should be rejected
    ]
    
    results = process_suggestions("+18633373705", test_suggestions)
    print(f"\nResults: {results}")
