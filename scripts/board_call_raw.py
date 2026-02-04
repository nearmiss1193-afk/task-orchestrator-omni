"""Board call: raw API output only"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''BOARD VALIDATION: Consolidated AI Memory System Proposal

Based on previous board input, here is the proposed implementation. Please validate or suggest improvements.

PROPOSED SUPABASE TABLES:
1. sovereign_config - Critical config (embed IDs, API keys, URLs, widget settings)
2. sovereign_actions - All actions taken with success/failure, input/output, timestamps
3. sovereign_errors - Error patterns with solutions (auto-lookup when same error occurs)
4. sovereign_code - Code snippets that worked (auto-retrieved for similar tasks)
5. sovereign_preferences - User corrections and preferences (hard rules)
6. sovereign_embeddings - Vector embeddings for semantic search (pgvector)

RETRIEVAL STRATEGY:
- Before ANY task: Query sovereign_config for relevant config
- Before ANY code edit: Query sovereign_code for similar patterns
- On ANY error: Query sovereign_errors for known solutions
- Always apply: sovereign_preferences as hard rules

REDUNDANCY MECHANISMS:
- Local file backup (GHL_EMBED_REFERENCE.md, operational_memory.md)
- Supabase as primary source of truth
- Auto-sync between file and DB on session start

QUESTIONS:
1. Is this schema complete? What's missing?
2. How should we implement the "query before action" hard rule?
3. What vector DB solution works best with Supabase?
4. Any redundancy mechanisms we're missing?

Give specific, actionable recommendations.'''

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
