"""Board call: raw API output only"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''Website issue report:
- Contact section uses Calendly/formsubmit.co, NOT GHL
- Sarah button loads alert, no call starts
- Floating icon only, no full widget

System state: working, sarah_status=minimalist_icon_v4, embed_source=supabase_locked

In 50 words or less: What is the root cause?'''

results = []

# Claude
print("=== CLAUDE ===")
print("curl -X POST https://api.anthropic.com/v1/messages")
try:
    r = requests.post('https://api.anthropic.com/v1/messages',
        headers={'x-api-key': os.environ.get('ANTHROPIC_API_KEY'), 'anthropic-version': '2023-06-01', 'content-type': 'application/json'},
        json={'model': 'claude-sonnet-4-20250514', 'max_tokens': 150, 'messages': [{'role': 'user', 'content': PROMPT}]}, timeout=60)
    data = r.json()
    resp = data.get('content', [{}])[0].get('text', str(data))
    print("RESPONSE:", resp)
    results.append({"ai": "Claude", "raw": resp})
except Exception as e:
    print("FAILED:", e)
    results.append({"ai": "Claude", "raw": f"FAILED: {e}"})

# Grok
print("\n=== GROK ===")
print("curl -X POST https://api.x.ai/v1/chat/completions")
try:
    r = requests.post('https://api.x.ai/v1/chat/completions',
        headers={'Authorization': 'Bearer ' + os.environ.get('GROK_API_KEY',''), 'Content-Type': 'application/json'},
        json={'model': 'grok-3', 'messages': [{'role': 'user', 'content': PROMPT}], 'max_tokens': 150}, timeout=60)
    data = r.json()
    resp = data.get('choices', [{}])[0].get('message', {}).get('content', str(data))
    print("RESPONSE:", resp)
    results.append({"ai": "Grok", "raw": resp})
except Exception as e:
    print("FAILED:", e)
    results.append({"ai": "Grok", "raw": f"FAILED: {e}"})

# Gemini
print("\n=== GEMINI ===")
print("curl -X POST https://generativelanguage.googleapis.com/.../gemini-2.0-flash:generateContent")
try:
    r = requests.post('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + os.environ.get('GEMINI_API_KEY',''),
        headers={'Content-Type': 'application/json'},
        json={'contents': [{'parts': [{'text': PROMPT}]}]}, timeout=60)
    data = r.json()
    resp = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', str(data))
    print("RESPONSE:", resp)
    results.append({"ai": "Gemini", "raw": resp})
except Exception as e:
    print("FAILED:", e)
    results.append({"ai": "Gemini", "raw": f"FAILED: {e}"})

# ChatGPT
print("\n=== CHATGPT ===")
print("curl -X POST https://api.openai.com/v1/chat/completions")
try:
    r = requests.post('https://api.openai.com/v1/chat/completions',
        headers={'Authorization': 'Bearer ' + os.environ.get('OPENAI_API_KEY',''), 'Content-Type': 'application/json'},
        json={'model': 'gpt-4o-mini', 'messages': [{'role': 'user', 'content': PROMPT}], 'max_tokens': 150}, timeout=60)
    data = r.json()
    resp = data.get('choices', [{}])[0].get('message', {}).get('content', str(data))
    print("RESPONSE:", resp)
    results.append({"ai": "ChatGPT", "raw": resp})
except Exception as e:
    print("FAILED:", e)
    results.append({"ai": "ChatGPT", "raw": f"FAILED: {e}"})

# Save
with open('board_call_raw.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\n=== DONE ===")
