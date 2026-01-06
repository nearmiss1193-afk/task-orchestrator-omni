
import os
import json
import urllib.request

# The key from user's screenshot
ANTHROPIC_KEY = "sk-ant-api03-Cuv78afM_sLScDw1gt3ZxhZ1JtUZuQSPKXt5Xi4ZZ0IMJLmgvHmVzBEKnWVe2rzqDgkGuytsGDdc6y_HBdOigw-mjYNggAA"

def test_claude(command):
    system_prompt = """You are the Sovereign AI Orchestrator for Empire Unified.
You help the Commander manage their AI business automation system.
Capabilities: SMS via GHL, Voice calls via Sarah (Vapi), Email via Resend.
Status: 5 leads, 142 AI calls tracked. All systems online. Sarah (Elite Voice AI) is active.
Be concise (under 80 words), helpful, action-oriented."""

    try:
        api_url = "https://api.anthropic.com/v1/messages"
        
        claude_payload = json.dumps({
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 200,
            "system": system_prompt,
            "messages": [{"role": "user", "content": command}]
        }).encode('utf-8')
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': ANTHROPIC_KEY,
            'anthropic-version': '2023-06-01'
        }
        
        req = urllib.request.Request(api_url, data=claude_payload, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as api_resp:
            result = json.loads(api_resp.read().decode('utf-8'))
            resp_text = result.get('content', [{}])[0].get('text', 'Command acknowledged.')
            return resp_text
    except Exception as e:
        return f"Error: {str(e)}"

print("Testing Claude API...")
result = test_claude("status?")
print(f"\nResult: {result}")
