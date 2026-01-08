import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Configuration
VAPI_PRIVATE_KEY = os.getenv("VAPI_PRIVATE_KEY")
GROK_API_KEY = os.getenv("GROK_API_KEY") 
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

from supabase import create_client

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        pass

def _get_cached(key):
    if not supabase: return None
    try:
        res = supabase.table('api_cache').select('value').eq('key', key).execute()
        if res.data:
            print(f"⚡ CACHE HIT: {key}")
            return res.data[0]['value']
    except:
        pass
    return None

def _set_cached(key, value):
    if not supabase: return
    try:
        supabase.table('api_cache').upsert({'key': key, 'value': value}).execute()
    except Exception as e:
        print(f"Cache Write Failed: {e}")

def execute_skill(task_type, payload):
    """
    Dispatcher for agent skills.
    Returns a dictionary or primitive that can be stored as JSON.
    """
    if task_type == 'make_call':
        return _make_vapi_call(payload)
    elif task_type == 'analyze_transcript':
        return _analyze_transcript(payload)
    elif task_type == 'send_email':
        return _send_email(payload)
    elif task_type == 'send_sms':
        return _send_sms(payload)
    elif task_type == 'find_email':
        return _find_email(payload)
    elif task_type == 'verify_email':
        return _verify_email(payload)
    else:
        raise ValueError(f"Unknown task_type: {task_type}")

def _make_vapi_call(payload):
    """
    Triggers a Vapi call.
    Payload expected: { 'phone': str, 'script_context': str, 'assistant_id': str }
    """
    phone = payload.get('phone')
    context = payload.get('script_context', '')
    assistant_id = payload.get('assistant_id') or os.getenv("VAPI_ASSISTANT_ID")
    
    if not phone:
        raise ValueError("Phone number required")

    headers = {
        "Authorization": f"Bearer {VAPI_PRIVATE_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "type": "outboundPhoneCall",
        "phoneNumberId": os.getenv("VAPI_PHONE_NUMBER_ID"), # Default outgoing number
        "customer": {"number": phone},
        "assistantId": assistant_id,
        "assistantOverrides": {
            "variableValues": {
                "context": context
            }
        }
    }
    
    response = requests.post("https://api.vapi.ai/call/phone", headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def _analyze_transcript(payload):
    """
    Analyzes transcript using Grok (or OpenAI compatible API).
    """
    transcript = payload.get('transcript')
    prompt = payload.get('prompt', "Summarize this call and extract action items.")
    
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "grok-beta", 
        "messages": [
            {"role": "system", "content": "You are a senior analyst."},
            {"role": "user", "content": f"{prompt}\n\nTranscript:\n{transcript}"}
        ],
        "temperature": 0.7
    }
    
    response = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def _send_sms(payload):
    """
    Sends SMS via GHL Webhook (or Twilio).
    """
    phone = payload.get('phone')
    message = payload.get('message')
    webhook_url = os.getenv("GHL_SMS_WEBHOOK")
    
    if not webhook_url:
        raise ValueError("GHL_SMS_WEBHOOK not set")
        
    data = {
        "phone": phone,
        "message": message
    }
    
    response = requests.post(webhook_url, json=data)
    response.raise_for_status()
    return {"status": "sent"}

def _send_email(payload):
    """
    Sends email via Resend.
    """
    to_email = payload.get('to')
    subject = payload.get('subject')
    html = payload.get('html')
    
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "from": "Empire AI <onboarding@resend.dev>", # Replace with verified domain
        "to": [to_email],
        "subject": subject,
        "html": f"<p style='background-color: #f3f4f6; padding: 10px; text-align: center; border-radius: 5px;'><a href='{os.getenv('APP_URL', 'http://localhost:8501')}' style='text-decoration: none; color: #3b82f6; font-weight: bold;'>⚡ View Agent Dashboard</a></p>" + html
    }
    
    response = requests.post("https://api.resend.com/emails", headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def _find_email(payload):
    """
    Finds email using Hunter.io via modules.hunter_verify (Cached)
    """
    first = payload.get('first_name')
    last = payload.get('last_name')
    domain = payload.get('domain')
    
    cache_key = f"find_email:{first}:{last}:{domain}".lower()
    cached = _get_cached(cache_key)
    if cached: return cached

    try:
        from modules import hunter_verify
    except ImportError:
        import hunter_verify
        
    result = hunter_verify.find_email(first, last, domain)
    
    if result:
        _set_cached(cache_key, result)
        
    return result

def _verify_email(payload):
    """
    Verifies email using Hunter.io via modules.hunter_verify (Cached)
    """
    email = payload.get('email')
    
    cache_key = f"verify_email:{email}".lower()
    cached = _get_cached(cache_key)
    if cached: return cached

    try:
        from modules import hunter_verify
    except ImportError:
        import hunter_verify
        
    result = hunter_verify.verify_email(email)
    
    if result:
        _set_cached(cache_key, result)
        
    return result
