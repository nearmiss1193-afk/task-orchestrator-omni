"""Board call: raw API output only"""
import os, json, requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''BOARD PROTOCOL: PageSpeed Optimization + Form UX Strategy

CONTEXT:
We are aiserviceco.com - an AI service company claiming to be smart, capable, and competent. 
Our PageSpeed Insights scores are embarrassingly low for an AI company:

CURRENT SCORES (Mobile):
- Performance: 62 (ORANGE)
- Accessibility: 92 (GREEN - good!)
- Best Practices: 73 (ORANGE)
- SEO: 58 (ORANGE)

PROBLEMS:
1. As an AI company, we should have ALL scores in 90s to demonstrate competence
2. SEO at 58 hurts discoverability and credibility
3. Performance at 62 means slow load times

UX ISSUE:
- Calendar and Contact forms are currently embedded INLINE (auto-opening)
- User wants BUTTONS that trigger MODALS instead
- Current behavior: User sees forms immediately without clicking
- Desired behavior: "Book Call" button → Opens modal with calendar
- Desired behavior: "Contact Us" button → Opens modal with form

QUESTIONS FOR THE BOARD:

1. **PAGESPEED PERFORMANCE (62 → 90+)**:
   - What are the biggest quick wins for performance?
   - Image optimization, lazy loading, code splitting?
   - Which iframes/scripts are hurting performance?

2. **SEO (58 → 90+)**:
   - What meta tags are we missing?
   - Structured data / JSON-LD needed?
   - Title/description optimization?

3. **BEST PRACTICES (73 → 90+)**:
   - Common issues causing this score?
   - HTTPS, console errors, deprecated APIs?

4. **FORM MODAL UX**:
   - User assessment: "Calendar and forms are just auto-opening" - correct?
   - Best practice: Inline embeds vs button-triggered modals?
   - User experience impact?

5. **PRIORITY ORDER**:
   - What should we fix first?
   - Which changes give biggest ROI?

Provide actionable, specific recommendations. We need to hit 90+ on ALL metrics.'''

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
