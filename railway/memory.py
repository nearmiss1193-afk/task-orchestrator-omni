"""
MEMORY MODULE - 3-Layer Memory Architecture
============================================
Layer A: contact_profiles (slow-changing facts)
Layer B: conversations + conversation_events (what happened)
Layer C: Working memory (compiled on-demand)
"""
import os
import re
import json
import requests
from datetime import datetime

# Supabase config - HARDCODED to match app.py (env var issues on Railway)
SUPABASE_URL = "https://rzcpfwkygdvoshtwxncs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")


def _supabase_request(method, table, data=None, params=None):
    """Internal Supabase request helper"""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=data, timeout=30)
        elif method == "PATCH":
            r = requests.patch(url, headers=headers, json=data, timeout=30)
        
        if not r.ok:
            print(f"[MEMORY] Supabase error {r.status_code}: {r.text[:200]}")
            return None
        
        if r.text.strip():
            return r.json()
        return True
    except Exception as e:
        print(f"[MEMORY] Exception: {e}")
        return None


# ============================================
# Phone Normalization (E.164)
# ============================================
def normalize_phone(phone):
    """Normalize phone number to E.164 format (+1XXXXXXXXXX)"""
    if not phone:
        return None
    
    # Strip all non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Handle US numbers
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    elif len(digits) > 10:
        # Already has country code
        return f"+{digits}"
    
    return phone  # Return as-is if can't normalize


# ============================================
# Contact Resolution (Identity Layer)
# ============================================
def resolve_or_create_contact(phone=None, email=None, ghl_id=None, company_name=None):
    """
    Find existing contact or create new one.
    Priority: ghl_id > phone > email
    Returns: contact dict with 'id'
    """
    contact = None
    
    # Try GHL ID first (most reliable)
    if ghl_id:
        result = _supabase_request("GET", "contact_profiles", params={
            "ghl_contact_id": f"eq.{ghl_id}",
            "limit": "1"
        })
        if result and len(result) > 0:
            return result[0]
    
    # Try normalized phone
    if phone:
        normalized = normalize_phone(phone)
        result = _supabase_request("GET", "contact_profiles", params={
            "phone": f"eq.{normalized}",
            "limit": "1"
        })
        if result and len(result) > 0:
            contact = result[0]
            # Update GHL ID if we have it now
            if ghl_id and not contact.get("ghl_contact_id"):
                _supabase_request("PATCH", f"contact_profiles?id=eq.{contact['id']}", {
                    "ghl_contact_id": ghl_id,
                    "updated_at": datetime.utcnow().isoformat()
                })
            return contact
    
    # Try email
    if email:
        result = _supabase_request("GET", "contact_profiles", params={
            "email": f"eq.{email}",
            "limit": "1"
        })
        if result and len(result) > 0:
            return result[0]
    
    # Create new contact
    new_contact = {
        "phone": normalize_phone(phone) if phone else None,
        "email": email,
        "ghl_contact_id": ghl_id,
        "company_name": company_name,
        "profile_json": {},
        "memory_summary": None
    }
    
    result = _supabase_request("POST", "contact_profiles", new_contact)
    if result and len(result) > 0:
        print(f"[MEMORY] Created contact: {result[0]['id']}")
        return result[0]
    
    return None


# ============================================
# Conversation Management
# ============================================
def get_or_create_conversation(contact_id, channel):
    """Get open conversation or create new one for this channel"""
    # Check for open conversation
    result = _supabase_request("GET", "conversations", params={
        "contact_id": f"eq.{contact_id}",
        "channel": f"eq.{channel}",
        "status": "eq.open",
        "order": "last_event_at.desc",
        "limit": "1"
    })
    
    if result and len(result) > 0:
        return result[0]
    
    # Create new conversation
    new_conv = {
        "contact_id": contact_id,
        "channel": channel,
        "status": "open"
    }
    result = _supabase_request("POST", "conversations", new_conv)
    if result and len(result) > 0:
        print(f"[MEMORY] Created {channel} conversation: {result[0]['id']}")
        return result[0]
    
    return None


# ============================================
# Event Logging (Append-Only)
# ============================================
def write_event(contact_id, event_type, source, external_id, payload, summary=None):
    """Write an event to the conversation log.
    Uses external_id to prevent duplicates.
    
    event_type: sms_in|sms_out|call_start|call_end|email_in|email_out|note|booking
    source: ghl|vapi|resend|system
    """
    # Defensive defaults for NOT NULL constraints
    if not event_type:
        event_type = "unknown"
    if not source:
        source = "system"
    if summary is None:
        summary = ""
    # Determine channel from event type
    if "sms" in event_type:
        channel = "sms"
    elif "call" in event_type:
        channel = "call"
    elif "email" in event_type:
        channel = "email"
    else:
        channel = "other"
    # Get or create conversation
    conv = get_or_create_conversation(contact_id, channel)
    if not conv:
        print(f"[MEMORY] Failed to get conversation for {contact_id}")
        return None
    # Ensure payload is a dict
    if not isinstance(payload, dict):
        payload = {"raw": payload}
    # Build event dict with required fields
    event = {
        "conversation_id": conv["id"],
        "event_type": event_type,
        "source": source,
        "external_id": external_id,
        "payload": payload,
        "summary": summary,
    }
    result = _supabase_request("POST", "conversation_events", event)
    if result:
        print(f"[MEMORY] Logged event: {event_type} from {source}")
        # Update conversation last_event_at
        _supabase_request("PATCH", f"conversations?id=eq.{conv['id']}", {
            "last_event_at": datetime.utcnow().isoformat()
        })
        # Trigger memory summary update (async in production)
        update_memory_summary(contact_id)
        return result[0] if isinstance(result, list) and len(result) > 0 else result
    return None


# ============================================
# Memory Retrieval (Layer C - Working Memory)
# ============================================
def get_memory(contact_id):
    """
    Compile working memory for next interaction.
    Returns dict with: memory_summary, recent_events, active_commitments
    """
    result = {
        "memory_summary": None,
        "recent_events": [],
        "active_commitments": []
    }
    
    # Get contact profile
    profile = _supabase_request("GET", "contact_profiles", params={
        "id": f"eq.{contact_id}",
        "limit": "1"
    })
    
    if profile and len(profile) > 0:
        result["memory_summary"] = profile[0].get("memory_summary")
        result["profile"] = profile[0].get("profile_json", {})
    
    # Get last 10 events across all conversations
    events = _supabase_request("GET", "conversation_events", params={
        "conversation_id": f"in.(select id from conversations where contact_id = '{contact_id}')",
        "order": "created_at.desc",
        "limit": "10"
    })
    
    # Fallback: get events via conversation lookup
    if not events:
        convs = _supabase_request("GET", "conversations", params={
            "contact_id": f"eq.{contact_id}"
        })
        if convs:
            conv_ids = [c["id"] for c in convs]
            for cid in conv_ids[:3]:  # Limit to 3 conversations
                ev = _supabase_request("GET", "conversation_events", params={
                    "conversation_id": f"eq.{cid}",
                    "order": "created_at.desc",
                    "limit": "5"
                })
                if ev:
                    result["recent_events"].extend(ev)
    else:
        result["recent_events"] = events
    
    # Extract summaries for quick context
    event_summaries = [
        e.get("summary") or f"[{e.get('event_type')}] {e.get('created_at', '')[:10]}"
        for e in result["recent_events"]
        if e.get("summary") or e.get("event_type")
    ]
    result["event_summaries"] = event_summaries
    
    # Check for active bookings/commitments in profile_json
    if result.get("profile"):
        commitments = result["profile"].get("active_commitments", [])
        result["active_commitments"] = commitments
    
    return result


def get_memory_context_string(contact_id):
    """
    Get a formatted string suitable for injecting into AI prompts.
    """
    mem = get_memory(contact_id)
    
    parts = []
    
    if mem.get("memory_summary"):
        parts.append(f"**Contact Summary**: {mem['memory_summary']}")
    
    if mem.get("event_summaries"):
        parts.append("**Recent Interactions**:")
        for s in mem["event_summaries"][:5]:
            parts.append(f"- {s}")
    
    if mem.get("active_commitments"):
        parts.append("**Active Commitments**:")
        for c in mem["active_commitments"]:
            parts.append(f"- {c}")
    
    return "\n".join(parts) if parts else "No prior context available."


# ============================================
# Memory Summarization (Gemini-powered)
# ============================================
def update_memory_summary(contact_id):
    """
    Update rolling memory summary using Gemini.
    Called after each event to keep summary fresh.
    """
    if not GEMINI_KEY:
        print("[MEMORY] No Gemini key, skipping summary update")
        return
    
    # Get current state
    mem = get_memory(contact_id)
    current_summary = mem.get("memory_summary") or "No prior summary."
    
    # Get latest events
    recent = mem.get("recent_events", [])[:5]
    event_text = "\n".join([
        f"- [{e.get('event_type')}] {e.get('summary') or json.dumps(e.get('payload', {}))[:100]}"
        for e in recent
    ])
    
    if not event_text:
        return  # Nothing new to summarize
    
    prompt = f"""Update this contact's memory summary with new events. Keep it factual, 2-3 sentences max.

CURRENT SUMMARY:
{current_summary}

NEW EVENTS:
{event_text}

OUTPUT only the updated summary, nothing else."""

    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 150}
            },
            timeout=15
        )
        
        if r.ok:
            new_summary = r.json().get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if new_summary:
                _supabase_request("PATCH", f"contact_profiles?id=eq.{contact_id}", {
                    "memory_summary": new_summary.strip(),
                    "updated_at": datetime.utcnow().isoformat()
                })
                print(f"[MEMORY] Updated summary for {contact_id}")
    except Exception as e:
        print(f"[MEMORY] Summary update failed: {e}")


# ============================================
# Job Locking (Scheduler Idempotency)
# ============================================
def acquire_job_lock(job_name, duration_seconds=300):
    """
    Try to acquire a lock for a scheduled job.
    Returns True if lock acquired, False if already locked.
    """
    now = datetime.utcnow()
    lock_until = datetime.utcnow().replace(
        second=now.second + duration_seconds
    ).isoformat()
    
    # Try to upsert - only succeeds if not currently locked
    try:
        result = _supabase_request("POST", "job_locks", {
            "job_name": job_name,
            "locked_until": lock_until,
            "locked_by": f"worker-{os.getpid()}"
        })
        
        if result:
            return True
        
        # Check if existing lock expired
        existing = _supabase_request("GET", "job_locks", params={
            "job_name": f"eq.{job_name}"
        })
        
        if existing and len(existing) > 0:
            lock_time = existing[0].get("locked_until")
            if lock_time and datetime.fromisoformat(lock_time.replace("Z", "")) < now:
                # Lock expired, claim it
                _supabase_request("PATCH", f"job_locks?job_name=eq.{job_name}", {
                    "locked_until": lock_until,
                    "locked_by": f"worker-{os.getpid()}"
                })
                return True
        
        return False
    except:
        return False


def release_job_lock(job_name):
    """Release a job lock"""
    _supabase_request("PATCH", f"job_locks?job_name=eq.{job_name}", {
        "locked_until": datetime.utcnow().isoformat()
    })
