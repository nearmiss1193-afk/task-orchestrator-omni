"""
LOCKED CONSTANTS - Python access to immutable configuration
These values CANNOT be changed by AI agents without human approval
"""
import yaml
import os

# Load from YAML
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "locked_constants.yaml")

def load_constants():
    """Load locked constants from YAML file"""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)["LOCKED_CONSTANTS"]

# Pre-load for direct import
_CONSTANTS = None

def get_constants():
    global _CONSTANTS
    if _CONSTANTS is None:
        try:
            _CONSTANTS = load_constants()
        except:
            # Fallback if YAML not available
            _CONSTANTS = FALLBACK_CONSTANTS
    return _CONSTANTS

# Fallback constants (in case YAML fails)
FALLBACK_CONSTANTS = {
    "company_name": "AI Service Co",
    "primary_persona": "Sarah",
    "pricing": {
        "starter_usd_per_month": 297,
        "lite_usd_per_month": 497,
        "growth_usd_per_month": 997,
        "enterprise": "custom",
        "trial_days": 14,
        "contract_terms": "No contracts. Cancel anytime."
    },
    "booking": {
        "appointment_name": "Sovereign Strategy Session",
        "appointment_duration_minutes": 15,
        "booking_link": "https://link.aiserviceco.com/discovery",
        "suggest_within_hours": 48,
        "lead_time_buffer_hours": 24,
        "calendar_name": "Empire Unified Master Calendar"
    },
    "escalation": {
        "owner_sms_phone_e164": "+13529368152",
        "ghl_task_priority": "High",
        "escalation_template": "🔥 [Vortex Intent] Lead: [Name] / Msg: [Message] / AI Draft: [Draft] / Link: [URL]."
    },
    "compliance": {
        "never_collect_payment_info": True,
        "emergency_instruction": "If you suspect a life-threatening emergency (gas leak, fire, CO alarm, etc.), hang up and dial 911 immediately.",
        "no_legal_or_insurance_advice": True,
        "opt_out_keyword": "STOP",
        "opt_out_action": "Tag as Unsubscribed and cease messaging."
    },
    "messaging_rules": {
        "sms_style": "1-2 short sentences; include booking link early when appropriate.",
        "call_style": "Professional dispatcher; calm, concise; confirm details then book."
    }
}

# Convenience accessors
def get_booking_link():
    return get_constants()["booking"]["booking_link"]

def get_escalation_phone():
    return get_constants()["escalation"]["owner_sms_phone_e164"]

def get_pricing():
    return get_constants()["pricing"]

def get_compliance():
    return get_constants()["compliance"]

def get_emergency_instruction():
    return get_constants()["compliance"]["emergency_instruction"]


if __name__ == "__main__":
    import json
    print("=" * 60)
    print("LOCKED CONSTANTS")
    print("=" * 60)
    print(json.dumps(get_constants(), indent=2))
