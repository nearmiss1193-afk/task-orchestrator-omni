#!/usr/bin/env python3
"""
Board Comprehensive Query: Two Topics
1. GHL vs Instantly (with full context that GHL is already warmed up)
2. Antigravity Memory/Consistency Improvement Recommendations
"""
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''BOARD STRATEGIC DECISION: Two Critical Topics

## TOPIC 1: GHL EMAIL - WITH CRITICAL NEW CONTEXT

### CONTEXT UPDATE - GHL IS ALREADY WARMED UP
Dan has clarified: "I have already passed the warm up in GoHighLevel so my deliverability is much higher."

This changes the equation. The previous board recommendation was to use Instantly.ai, but that assumed we'd need to warm up from scratch.

### Current Technical Issue (What's Actually Broken):
1. GHL Webhooks return HTTP 200 "Success" but emails are NOT delivered
2. The webhook accepts the request but the GHL workflow doesn't actually send
3. GHL API direct access: DOESN'T WORK (private integration - verified)
4. Browser automation (Playwright): Failed due to login timeout/2FA

### GHL Credentials Available:
- Email: nearmiss1193@gmail.com
- Password: Inez11752990@
- Location ID: RnK4OjX0oDcqtWw0VyLr

### The Real Question Now:
Given that GHL is ALREADY WARMED UP with good deliverability:
1. Should we invest time fixing the webhook → workflow issue in GHL?
2. Is it worth learning GHL automation properly (browser or API)?
3. Or is Instantly still better despite losing the warmup advantage?

### What Needs to Be Fixed in GHL:
The webhook triggers but the email action doesn't execute. Possible causes:
- Workflow is in DRAFT mode (not published)
- Email action misconfigured
- Missing email template
- Account-level sending restrictions

### Board Question for Topic 1:
**Given GHL is already warmed up, what is the most efficient path to get cold emails actually delivering?**

---

## TOPIC 2: ANTIGRAVITY AI MEMORY & CONSISTENCY IMPROVEMENT

### Session Problems Observed Today:
1. **Forgot GHL API doesn't work** - Tried API approach despite user confirming webhooks are required
2. **Forgot GHL credentials** - Had to be reminded credentials exist in .env
3. **Used wrong webhook URL** - reliable_email.py has different URL than .env
4. **Didn't recall past lessons** - Repeated mistakes from previous sessions
5. **Didn't check operational_memory.md first** - Critical info was already documented

### Current Memory System:
- `operational_memory.md` - Contains hard rules and session learnings
- `agent_memory.json` - Stores configuration and triggers
- User global rules - Defines Antigravity behavior

### Problems with Current Approach:
1. Antigravity doesn't consistently read operational_memory.md before acting
2. Learned lessons aren't being retained across sessions
3. Same mistakes get repeated (GHL API, credentials, webhooks)
4. Not building on past work intelligently

### Board Questions for Topic 2:
1. What memory architecture would make Antigravity truly autonomous and consistent?
2. How should operational memories be structured for optimal recall?
3. What triggers should force Antigravity to check memory before acting?
4. How can past mistakes become permanent learning (not repeated)?
5. What are best practices for AI agent memory in 2026?

---

## EXPECTED OUTPUT FORMAT:

### TOPIC 1 RESPONSE:
1. Given GHL warmup exists: Fix GHL or switch to Instantly?
2. If fix GHL: Specific steps to debug the webhook → email workflow
3. Time estimate for each approach
4. Recommendation with rationale

### TOPIC 2 RESPONSE:
1. Recommended memory architecture for Antigravity
2. Specific changes to operational_memory.md structure
3. Workflow changes to ensure memory is always consulted
4. Techniques for persistent learning across sessions
5. Concrete implementation steps
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
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": PROMPT}],
            },
            timeout=180,
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
            json={"model": "grok-3-latest", "messages": [{"role": "user", "content": PROMPT}], "max_tokens": 4000},
            timeout=180,
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
            timeout=180,
        )
        data = response.json()
        return {"ai": "Gemini", "raw": data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", str(data))}
    except Exception as e:
        return {"ai": "Gemini", "raw": f"ERROR: {e}"}

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    print("=" * 60)
    print("BOARD QUERY: GHL Fix + Memory Improvement")
    print("=" * 60)
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(query_claude),
            executor.submit(query_grok),
            executor.submit(query_gemini),
        ]
        results = [f.result() for f in futures]
    
    output_file = "board_comprehensive_response.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print("\n" + "=" * 60)
    
    for r in results:
        print(f"\n=== {r['ai']} ===")
        print(r['raw'][:4000] + "..." if len(r['raw']) > 4000 else r['raw'])
        print("-" * 60)
    
    print("\n=== BOARD CONSULTATION COMPLETE ===")
