#!/usr/bin/env python3
"""Board Protocol: Query all AIs for strategic decision."""
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''BOARD QUERY: Impact of Delaying GA4/Clarity Scripts

## Context
We are AI Service Co - an AI automation agency with a website at aiserviceco.com.

**Current Implementation:**
- GA4 (Google Analytics 4) loads 3 seconds after page load
- Microsoft Clarity loads 3 seconds after page load
- Both are analytics/tracking tools

**Proposed Change (Option A):**
- Delay GA4 and Clarity to load 5 seconds after page load (instead of 3)

## Questions for the Board

1. **What data/tracking would we lose with 5s delay vs 3s delay?**
   - Bounce rate accuracy?
   - Session recording completeness?
   - User behavior data?

2. **What is the typical user behavior timeline?**
   - How long do users typically wait before interacting?
   - At what point would delayed tracking miss critical data?

3. **Is 5 seconds too aggressive or not aggressive enough?**
   - Some recommend 5-10 second delays for performance
   - What's the sweet spot for analytics accuracy vs performance?

4. **Are there alternative approaches?**
   - Load on user interaction instead of timeout?
   - Use lighter analytics alternatives?

5. **What's the actual PageSpeed benefit?**
   - Will going from 3s to 5s make a measurable difference?
   - Or is the benefit diminishing returns at that point?

Give specific, data-driven recommendations.
'''

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
