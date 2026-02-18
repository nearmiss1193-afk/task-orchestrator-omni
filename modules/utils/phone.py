import re

def normalize_phone(raw_phone: str) -> str:
    """
    Standardize phone to E.164 format: +1XXXXXXXXXX
    Used by BOTH vapi_webhook and sms_inbound for consistency.
    Board mandate: prevent format mismatch causing memory lookup failures.
    """
    if not raw_phone:
        return ""
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', raw_phone)
    
    # Handle US numbers
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    elif len(digits) > 11:
        # Assume it already has a country code if > 11 digits
        return f"+{digits}"
    
    # Fallback for short or non-standard strings
    return f"+{digits}" if digits else raw_phone
