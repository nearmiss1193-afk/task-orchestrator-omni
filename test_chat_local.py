
import os
import json
import re
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

def test_chat(command):
    """Test the chat logic locally"""
    resp_text = "Command received."
    cmd_lower = command.lower()
    
    # ACTION: Send SMS
    if any(x in cmd_lower for x in ["send sms", "text ", "message "]):
        resp_text = "SMS command detected"
    
    # ACTION: Call
    elif any(x in cmd_lower for x in ["call ", "dial ", "phone "]):
        resp_text = "Call command detected"
    
    # ACTION: Email
    elif "email" in cmd_lower:
        resp_text = "Email command detected"
    
    # STATUS/INFO: Use Gemini via HTTP
    else:
        GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
        if GEMINI_KEY:
            try:
                system_prompt = """You are the Sovereign AI Orchestrator for Empire Unified.
You help the Commander manage their AI business automation system.
Capabilities: SMS via GHL, Voice calls via Sarah (Vapi), Email via Resend.
Status: 5 leads, 142 AI calls tracked. All systems online. Sarah (Elite Voice AI) is active.
Be concise (under 80 words), helpful, action-oriented."""

                prompt_text = f"{system_prompt}\n\nCommander: {command}"
                
                api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                
                gemini_payload = json.dumps({
                    "contents": [{"parts": [{"text": prompt_text}]}]
                }).encode('utf-8')
                
                req = urllib.request.Request(api_url, data=gemini_payload, headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=10) as api_resp:
                    result = json.loads(api_resp.read().decode('utf-8'))
                    resp_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Command acknowledged.')
            except Exception as gemini_err:
                resp_text = f"System operational. (AI note: {str(gemini_err)[:40]})"
        else:
            resp_text = "System online. Gemini key not configured."
    
    return resp_text

print("Testing chat locally...")
print("Result:", test_chat("status"))
