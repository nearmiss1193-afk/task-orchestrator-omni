#!/usr/bin/env python3
"""Board Protocol: Query all AIs for strategic decision."""
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''STRATEGIC BOARD QUERY: Operational Excellence & PageSpeed 90+

## CURRENT STATE (Feb 4, 2026)
- Performance: Mobile 77, Desktop 81
- Accessibility: 92 ✅
- Best Practices: 73 (STUCK despite error suppression)
- SEO: 92

## QUESTIONS FOR THE BOARD:

### 1. SUPABASE SYNC FOR OPERATIONAL MEMORY
Currently we have `operational_memory.md` in git. Should we sync this to Supabase so Modal webhooks can read the latest memory?

Options:
A) Create `sovereign_memory` table in Supabase
B) Use Supabase Edge Functions to read from git
C) Keep as file-only (current)
D) Other approach?

**What gives us the BEST:**
- Operational awareness
- Operational capabilities
- Operational competency
- Operational memory for daily tasks and customer handling

### 2. WHAT TO DO ABOUT payment.html?
We have a payment.html file but user says we don't have a payment page anymore. Options:
A) Delete it
B) Keep for future use
C) Redirect to checkout
D) Archive it

### 3. BEST PRACTICES 73 → 90+
Error suppression was added but BP is still 73. What else?
- Should we go nuclear (remove Clarity/GA4/Vapi)?
- Any other fixes we're missing?

### 4. SEO 92 → 100
What specific fixes would push SEO from 92 to 100?
- Missing meta tags?
- Structured data improvements?
- Performance impact on SEO?

### 5. PERFORMANCE 77-81 → 90+
Key blockers for performance?
- YouTube embeds (lazy loaded already)
- Third-party scripts
- Image optimization
- Code splitting

PROVIDE SPECIFIC, ACTIONABLE RECOMMENDATIONS WITH CODE EXAMPLES WHERE APPLICABLE.'''

def query_claude():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"ai": "Claude", "raw": "ERROR: No ANTHROPIC_API_KEY"}
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2500,
                "messages": [{"role": "user", "content": PROMPT}],
            },
            timeout=120,
        )
        data = response.json()
        return {"ai": "Claude", "raw": data.get("content", [{}])[0].get("text", str(data))}
    except Exception as e:
        return {"ai": "Claude", "raw": f"ERROR: {e}"}

def query_grok():
    api_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    if not api_key:
        return {"ai": "Grok", "raw": "ERROR: No GROK_API_KEY or XAI_API_KEY"}
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "grok-3-latest", "messages": [{"role": "user", "content": PROMPT}]},
            timeout=120,
        )
        data = response.json()
        return {"ai": "Grok", "raw": data.get("choices", [{}])[0].get("message", {}).get("content", str(data))}
    except Exception as e:
        return {"ai": "Grok", "raw": f"ERROR: {e}"}

def query_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"ai": "Gemini", "raw": "ERROR: No GEMINI_API_KEY"}
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": PROMPT}]}]},
            timeout=120,
        )
        data = response.json()
        return {"ai": "Gemini", "raw": data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", str(data))}
    except Exception as e:
        return {"ai": "Gemini", "raw": f"ERROR: {e}"}

def query_chatgpt():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"ai": "ChatGPT", "raw": "ERROR: No OPENAI_API_KEY"}
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-4o", "messages": [{"role": "user", "content": PROMPT}]},
            timeout=120,
        )
        data = response.json()
        return {"ai": "ChatGPT", "raw": data.get("choices", [{}])[0].get("message", {}).get("content", str(data))}
    except Exception as e:
        return {"ai": "ChatGPT", "raw": f"ERROR: {e}"}

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    print("Querying Board: Operational Excellence...")
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(query_claude),
            executor.submit(query_grok),
            executor.submit(query_gemini),
            executor.submit(query_chatgpt),
        ]
        results = [f.result() for f in futures]
    
    with open("board_call_raw.json", "w") as f:
        json.dump(results, f, indent=2)
    
    for r in results:
        print(f"=== {r['ai']} ===")
        print(r['raw'][:2000] + "..." if len(r['raw']) > 2000 else r['raw'])
    
    print("\n=== DONE ===")
