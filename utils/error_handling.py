"""
MISSION: ERROR HARDENING UTILITIES
Strict validation for all DB and webhook operations
"""

def check_supabase_error(response, operation_name: str = "DB Operation"):
    """
    Validates Supabase response and raises exception if error detected.
    
    Args:
        response: Supabase response object
        operation_name: Description of operation for error context
    
    Raises:
        Exception: If response contains an error
    """
    if hasattr(response, 'error') and response.error:
        error_msg = f"{operation_name} FAILED: {response.error}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    return response


def validate_webhook_response(response, webhook_name: str = "Webhook"):
    """
    Validates HTTP response from webhook and raises exception on failure.
    
    Args:
        response: requests.Response object
        webhook_name: Description of webhook for error context
    
    Raises:
        Exception: If status code indicates failure
    
    Returns:
        bool: True if successful
    """
    if response.status_code not in [200, 201, 204]:
        error_msg = f"{webhook_name} FAILED: HTTP {response.status_code} - {response.text[:200]}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)
    
    print(f"✅ {webhook_name} SUCCESS: HTTP {response.status_code}")
    return True


def brain_log(supabase, message: str, level: str = "INFO"):
    """
    Unified logging utility for all Modal workers.
    
    Args:
        supabase: Supabase client instance
        message: Log message
        level: Log level (INFO, WARN, ERROR, CRITICAL)
    """
    import datetime
    try:
        supabase.table("brain_logs").insert({
            "message": message,
            "level": level,
            "timestamp": datetime.datetime.now().isoformat()
        }).execute()
        print(f"[{level}] {message}")
    except Exception as e:
        print(f"⚠️ Logging failed: {e}")
