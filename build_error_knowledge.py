"""
🔍 ERROR KNOWLEDGE BUILDER
==========================
Scans all known errors, generates fixes, and stores in knowledge base.
Creates a learning system from all past failures.
"""
import os
import json
import re
from datetime import datetime
from modules.self_healer import SelfHealingAgent
from dotenv import load_dotenv
load_dotenv()

# Initialize healer
healer = SelfHealingAgent()

# === KNOWN ERRORS FROM MODAL LOGS (extracted from screenshots) ===
KNOWN_ERRORS = [
    {
        "source": "cloud_multi_touch",
        "error_type": "AttributeError",
        "error_message": "'NoneType' object has no attribute 'get'",
        "file_path": "/root/modal_deploy.py",
        "line_number": 673,
        "function_name": "cloud_multi_touch",
        "context": {
            "cause": "meta variable was None when trying to call meta.get('email')",
            "lead_count": 5
        },
        "stack_trace": """Traceback (most recent call last):
  File "/pkg/modal/_runtime/container_io_manager.py", line 947, in handle_input_exception
    yield
  File "/pkg/modal/_container_entrypoint.py", line 171, in run_input_sync
    values = io_context.call_function_sync()
  File "/pkg/modal/_runtime/container_io_manager.py", line 225, in call_function_sync
    expected_value_or_values = self.finalized_function.callable(*args, **kwargs)
  File "/root/modal_deploy.py", line 673, in cloud_multi_touch
    email = meta.get("email") or lead.get("email")
AttributeError: 'NoneType' object has no attribute 'get'"""
    },
    {
        "source": "cloud_prospector",
        "error_type": "HTTPError",
        "error_message": "422 Unprocessable Entity - Apollo rate limit exceeded",
        "file_path": "/root/modal_deploy.py",
        "line_number": 445,
        "function_name": "cloud_prospector",
        "context": {
            "cause": "Apollo API rate limit (422 error)",
            "api": "apollo.io"
        },
        "stack_trace": """requests.exceptions.HTTPError: 422 Client Error: Unprocessable Entity"""
    },
    {
        "source": "cloud_drip_campaign",
        "error_type": "KeyError",
        "error_message": "'company_name'",
        "file_path": "/root/modal_deploy.py",
        "line_number": 580,
        "function_name": "cloud_drip_campaign",
        "context": {
            "cause": "Lead dict missing 'company_name' key"
        },
        "stack_trace": """KeyError: 'company_name'"""
    },
    {
        "source": "vapi_caller",
        "error_type": "ValueError",
        "error_message": "Invalid phone number format",
        "file_path": "/root/modal_deploy.py",
        "line_number": 320,
        "function_name": "make_vapi_call",
        "context": {
            "cause": "Phone number had invalid format (less than 10 digits)"
        },
        "stack_trace": """ValueError: Invalid phone number format"""
    },
    {
        "source": "email_sender",
        "error_type": "ConnectionError",
        "error_message": "Resend API connection timeout",
        "file_path": "/root/modal_deploy.py",
        "line_number": 410,
        "function_name": "send_email",
        "context": {
            "cause": "Network timeout to Resend API"
        },
        "stack_trace": """requests.exceptions.ConnectionError: Connection timed out"""
    }
]

# === KNOWN FIXES (pre-built knowledge) ===
KNOWN_FIXES = {
    "AttributeError_NoneType_get": {
        "pattern": "'NoneType' object has no attribute 'get'",
        "root_cause": "Variable was None instead of dict when trying to access .get() method",
        "fix_suggestion": """
# Always ensure variable is a dict before calling .get()
if not meta or not isinstance(meta, dict):
    meta = {}
# Then safely access
value = meta.get("key", "default")
""",
        "prevention_tip": "Add null checks before any .get() calls on potentially None variables",
        "confidence": 0.95
    },
    "Apollo_422_RateLimit": {
        "pattern": "422 Unprocessable Entity",
        "root_cause": "Apollo.io API rate limit exceeded (~2000 requests/day on free tier)",
        "fix_suggestion": """
# Add rate limiting and retry logic
import time
def apollo_request_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        resp = requests.post(url, json=data)
        if resp.status_code == 422:
            wait = 60 * (attempt + 1)  # Exponential backoff
            print(f"Rate limited, waiting {wait}s...")
            time.sleep(wait)
        else:
            return resp
    return None
""",
        "prevention_tip": "Implement request pacing (max 1 request/second) and fallback data sources",
        "confidence": 0.9
    },
    "KeyError_Missing_Field": {
        "pattern": "KeyError",
        "root_cause": "Trying to access dict key that doesn't exist",
        "fix_suggestion": """
# Use .get() with defaults instead of direct access
company = lead.get("company_name", "Unknown Company")
# Or validate before access
if "company_name" not in lead:
    continue  # Skip this lead
""",
        "prevention_tip": "Always use .get() with defaults for optional fields",
        "confidence": 0.95
    },
    "ValueError_Phone_Format": {
        "pattern": "Invalid phone number",
        "root_cause": "Phone number validation failed due to incorrect format",
        "fix_suggestion": """
def validate_phone(phone_str):
    if not phone_str:
        return False, None, "No phone"
    cleaned = re.sub(r'\\D', '', str(phone_str))
    if len(cleaned) < 10:
        return False, None, "Too short"
    if cleaned[-7:-4] == "555":
        return False, None, "Fake 555 number"
    return True, f"+1{cleaned[-10:]}", None
""",
        "prevention_tip": "Always validate and clean phone numbers before calling APIs",
        "confidence": 0.95
    },
    "ConnectionError_Timeout": {
        "pattern": "Connection timed out",
        "root_cause": "Network request timed out - server too slow or offline",
        "fix_suggestion": """
# Add timeout and retry logic
def api_request_with_retry(url, data, timeout=30, max_retries=3):
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=data, timeout=timeout)
            return resp
        except requests.exceptions.Timeout:
            print(f"Timeout, retry {attempt + 1}/{max_retries}")
            time.sleep(2 ** attempt)
    return None
""",
        "prevention_tip": "Always set timeout on requests and implement retry logic",
        "confidence": 0.9
    }
}


def load_previous_errors():
    """Load all known errors into the database"""
    print("="*60)
    print("🔍 LOADING PREVIOUS ERRORS INTO KNOWLEDGE BASE")
    print("="*60)
    
    logged_count = 0
    for error in KNOWN_ERRORS:
        try:
            # Insert into database
            result = healer.client.table("error_logs").insert({
                "source": error["source"],
                "error_type": error["error_type"],
                "error_message": error["error_message"],
                "file_path": error.get("file_path"),
                "line_number": error.get("line_number"),
                "function_name": error.get("function_name"),
                "stack_trace": error.get("stack_trace", ""),
                "context": error.get("context", {})
            }).execute()
            
            if result.data:
                logged_count += 1
                print(f"✅ Logged: {error['source']} → {error['error_type']}")
        except Exception as e:
            print(f"⚠️ Already exists or error: {e}")
    
    print(f"\n📊 Logged {logged_count} historical errors")
    return logged_count


def generate_all_fixes():
    """Generate fixes for all unfixed errors"""
    print("\n" + "="*60)
    print("🔧 GENERATING FIXES FOR ALL ERRORS")
    print("="*60)
    
    # Get all errors without fixes
    errors = healer.client.table("error_logs") \
        .select("*") \
        .is_("fix_suggested", "null") \
        .execute()
    
    if not errors.data:
        print("✅ No unfixed errors found!")
        return 0
    
    fixed_count = 0
    for error in errors.data:
        error_msg = error.get("error_message", "")
        
        # First check known fixes
        fix_applied = False
        for fix_key, fix_data in KNOWN_FIXES.items():
            if fix_data["pattern"] in error_msg:
                # Apply known fix
                healer.client.table("error_logs").update({
                    "fix_suggested": json.dumps({
                        "root_cause": fix_data["root_cause"],
                        "fix_suggestion": fix_data["fix_suggestion"],
                        "prevention_tip": fix_data["prevention_tip"],
                        "confidence": fix_data["confidence"],
                        "source": "knowledge_base"
                    })
                }).eq("id", error["id"]).execute()
                
                print(f"✅ Applied known fix: {error['source']} → {fix_key}")
                fixed_count += 1
                fix_applied = True
                break
        
        # If no known fix, generate with Claude
        if not fix_applied:
            print(f"🤖 Generating AI fix for: {error['source']}")
            fix = healer.generate_fix(error["id"])
            if fix:
                fixed_count += 1
    
    print(f"\n📊 Generated {fixed_count} fixes")
    return fixed_count


def build_knowledge_document():
    """Create a knowledge base document from all fixes"""
    print("\n" + "="*60)
    print("📚 BUILDING KNOWLEDGE BASE DOCUMENT")
    print("="*60)
    
    # Get all errors with fixes
    errors = healer.client.table("error_logs") \
        .select("*") \
        .not_.is_("fix_suggested", "null") \
        .order("created_at", desc=True) \
        .execute()
    
    if not errors.data:
        print("No fixes found to document")
        return
    
    # Generate markdown document
    doc = """# 🧠 Error Knowledge Base

This document contains all known errors and their fixes, auto-generated by the Self-Healing AI system.

---

"""
    
    for error in errors.data:
        try:
            fix = json.loads(error.get("fix_suggested", "{}"))
        except:
            fix = {}
        
        doc += f"""## {error['error_type']}: {error['source']}

**Error Message**: `{error['error_message']}`

**Location**: `{error.get('file_path', 'Unknown')}:{error.get('line_number', '?')}`

**Root Cause**: {fix.get('root_cause', 'Unknown')}

**Fix**:
```python
{fix.get('fix_suggestion', 'No fix available')}
```

**Prevention**: {fix.get('prevention_tip', 'N/A')}

**Confidence**: {fix.get('confidence', 0) * 100:.0f}%

---

"""
    
    # Save to knowledge base
    kb_path = "knowledge_base/error_fixes.md"
    os.makedirs("knowledge_base", exist_ok=True)
    
    with open(kb_path, "w", encoding="utf-8") as f:
        f.write(doc)
    
    print(f"✅ Knowledge base saved to: {kb_path}")
    return kb_path


def main():
    """Main entry point"""
    print("\n" + "🧠"*30)
    print("  ERROR KNOWLEDGE BUILDER - LEARNING FROM ALL FAILURES")
    print("🧠"*30 + "\n")
    
    # Step 1: Load previous errors
    load_previous_errors()
    
    # Step 2: Generate fixes
    generate_all_fixes()
    
    # Step 3: Build knowledge document
    build_knowledge_document()
    
    # Step 4: Run healing cycle
    print("\n" + "="*60)
    print("🔄 RUNNING SELF-HEAL CYCLE")
    print("="*60)
    healer.self_heal_cycle(hours=168)  # Last week
    
    print("\n" + "="*60)
    print("✅ KNOWLEDGE BASE COMPLETE!")
    print("="*60)
    print("\nThe system has learned from all previous errors.")
    print("Future errors will be auto-diagnosed and fixed.")


if __name__ == "__main__":
    main()
