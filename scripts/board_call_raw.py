#!/usr/bin/env python3
"""Board Protocol: Query all AIs for strategic decision."""
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''EMERGENCY DIAGNOSIS: Best Practices STUCK at 73 Despite Security Headers

SITUATION:
We added security headers to aiserviceco.com but Best Practices is STILL 73.

CURRENT SCORES (Desktop):
- Performance: 76 (was 82, dropped)
- Accessibility: 92 ✅
- Best Practices: 73 (STUCK - won't move)
- SEO: 92 ✅

WHAT WE ALREADY ADDED:
- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN  
- Referrer-Policy: strict-origin-when-cross-origin
- DNS prefetch for fonts, CDN, etc
- rel="noopener noreferrer" on all external links
- All scripts already use defer or async
- YouTube iframes have lazy loading + titles

WHY IS BEST PRACTICES STUCK AT 73?

Board, I need you to diagnose the EXACT remaining issues:

1. **What are the ONLY remaining Best Practices audit items?**
   - List each one specifically
   - What % weight does each carry?

2. **Third-party scripts?**
   - We have: Vapi widget, Microsoft Clarity, Google Analytics, YouTube embeds
   - Which of these is hurting Best Practices?
   - Can we defer/async them better?

3. **Console errors?**
   - What specific JS errors would cause -27 points?
   - How do I check without access to browser console?

4. **Vercel/CDN headers?**
   - Do meta http-equiv work for security headers on Vercel?
   - Or do we need vercel.json headers config?

5. **EXACT CODE to push 73 → 90+**
   - Be surgical
   - Tell me exactly what to add/remove/change

Target: Best Practices 90+, ALL metrics 90+'''

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
                "max_tokens": 2000,
                "messages": [{"role": "user", "content": PROMPT}],
            },
            timeout=120,
        )
        data = response.json()
        return {"ai": "Claude", "raw": data.get("content", [{}])[0].get("text", str(data))}
    except Exception as e:
        return {"ai": "Claude", "raw": f"ERROR: {e}"}

def query_grok():
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        return {"ai": "Grok", "raw": "ERROR: No XAI_API_KEY"}
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
    print("Querying Board: Best Practices 73 Diagnosis...")
    
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
        print(r['raw'][:1000] + "..." if len(r['raw']) > 1000 else r['raw'])
    
    print("\n=== DONE ===")
