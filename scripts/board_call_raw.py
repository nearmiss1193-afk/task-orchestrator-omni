#!/usr/bin/env python3
"""Board Protocol: Query all AIs for strategic decision."""
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''BOARD PROTOCOL: SEO Score 61 → 100 Emergency

CONTEXT:
We just optimized aiserviceco.com for PageSpeed Insights:
- Added OG meta tags (og:title, og:description, og:image, og:url, og:type)
- Added Twitter Card tags
- Added JSON-LD structured data (Organization, Service)
- Added canonical URL
- Improved title and meta description
- Converted inline iframes to lazy-loaded modal buttons

CURRENT SCORES (after first round of fixes):
- Performance: 75-79 (was 62) ⬆️
- Accessibility: 92 ✅
- Best Practices: 73 (no change)
- SEO: 61 (was 58) ⬆️ BUT STILL FAILING

USER REQUIREMENT:
"We need to be in 90s on all 4, especially SEO - I want us up close to 100"

QUESTIONS FOR THE BOARD:

1. **SEO: 61 → 100**:
   - What specific items are typically failed in Lighthouse SEO audits?
   - What are the TOP missing items we haven't implemented yet?
   - robots.txt? sitemap.xml? hreflang? lang attribute?
   - Image alt text? Link descriptions?
   - Is our structured data complete?

2. **BEST PRACTICES: 73 → 90+**:
   - Console errors?
   - Deprecated APIs?
   - External links without rel="noopener"?
   - What common issues drop this score?

3. **PERFORMANCE: 75 → 90+**:
   - After lazy loading iframes, what else?
   - Font loading? Critical CSS?
   - Image format/compression?

4. **CHECKLIST**:
   - Give me a concrete checklist of exactly what to add/fix

Be SPECIFIC. No general advice. Tell me exactly what code/files to add.'''

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
    print("=== CLAUDE ===")
    print(f"curl -X POST https://api.anthropic.com/v1/messages")
    print("=== GROK ===")
    print(f"curl -X POST https://api.x.ai/v1/chat/completions")
    print("=== GEMINI ===")
    print(f"curl -X POST https://generativelanguage.googleapis.com/...")
    print("=== CHATGPT ===")
    print(f"curl -X POST https://api.openai.com/v1/chat/completions")
    
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
        print(r['raw'][:500] + "..." if len(r['raw']) > 500 else r['raw'])
    
    print("=== DONE ===")
