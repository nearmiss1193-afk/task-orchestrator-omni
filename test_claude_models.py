
import os
import json
import urllib.request
from dotenv import load_dotenv

load_dotenv()

# Read from environment - NEVER hardcode API keys
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Try claude-3-sonnet-20240229 instead (more stable model name)
def test_claude(command, model_name):
    system_prompt = """You are the Sovereign AI Orchestrator. Be concise."""

    try:
        api_url = "https://api.anthropic.com/v1/messages"
        
        claude_payload = json.dumps({
            "model": model_name,
            "max_tokens": 100,
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
            resp_text = result.get('content', [{}])[0].get('text', 'OK')
            return f"SUCCESS with {model_name}: {resp_text[:100]}"
    except Exception as e:
        return f"FAILED {model_name}: {str(e)[:50]}"

print("Testing different Claude models...")
models = [
    "claude-3-5-sonnet-20241022",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307"
]

for m in models:
    print(f"\n{m}:")
    print(test_claude("hello", m))
