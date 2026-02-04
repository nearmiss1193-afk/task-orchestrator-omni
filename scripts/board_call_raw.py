"""Board call: raw API output only"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''BOARD PROTOCOL: Hero Section Links - Comprehensive Fix

CONTEXT:
We have multiple link/button issues in the hero section of aiserviceco.com. The Vapi widget (bottom-right orange pill) is working correctly.

ISSUE 1 (Previously Discussed):
- CENTER orange "Call Sarah AI (Voice)" BUTTON shows alert popup
- Board consensus: Option A - Make it activate Vapi widget directly

ISSUE 2 (NEW):
- The TEXT LINK "📞 Call Sarah (Voice AI): Talk to Sarah (Voice AI)"
- When clicked, shows browser popup "Open Phone Link?"
- This is because it's using a tel: link (href="tel:+18632132505")
- User does NOT want phone app to open
- User wants it to either activate Vapi OR be removed/replaced

QUESTION FOR THE BOARD:
1. Should this link activate Vapi or be removed entirely?
2. If kept: How to make text link trigger Vapi (onclick vs href)?
3. Having both a tel: link AND Vapi is confusing - which is better UX?
4. Overall hero section strategy: What's the cleanest layout?

Current hero section elements:
- [Button] "Talk to Sarah (Voice AI)" → shows alert
- [Link] "📞 Call Sarah (Voice AI): Talk to Sarah (Voice AI)" → shows phone popup
- [Link] "💬 Text Sarah: +1 (352) 758-5336" → SMS link
- [Link] "👨‍💼 Talk to Dan (Human): +1 (352) 936-8152" → phone link
- [Widget] Vapi pill (bottom-right) → WORKS

Give focused suggestions for the cleanest UX.'''

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
