#!/usr/bin/env python3
"""Board Review: Owner's Improvement Suggestions for Email Outreach."""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

PROMPT = """BOARD VOTE REQUIRED: Owner's Email Outreach Improvements

## CONTEXT
Dan (owner) has authorized sending Batch 1 emails but provided specific feedback for future improvements. We need 3/4 board agreement to implement these as standard operating procedure.

## OWNER'S FEEDBACK (Feb 5, 2026)

### Issue 1: "Dear Team" Problem
Current emails say "Dear Team" when we don't have a contact name. Dan wants:
- Find actual contact names before sending
- Research business owner/manager names
- Never send to "Dear Team" in future batches

### Issue 2: PDF Audit Report Not Comprehensive Enough
Current PDF only repeats what the email says. Dan wants comprehensive audits that include:

**A. Additional Services We Can Offer:**
1. Internal office systems:
   - Dispatch management
   - Payroll handling
   - Company newsletters for customer retention
   
2. Digital marketing:
   - Google Business Profile upgrades and monitoring
   - Facebook management
   - Instagram management
   
3. Customer retention:
   - Newsletter to keep customers informed
   - Referral program setup
   - Long-term engagement strategies

**B. Problems They May Be Encountering:**
- Current issues hurting their business
- Future risks they should be aware of
- Competition analysis

**C. Benefits of Newsletter/Retention:**
- Customers remember them for referrals
- First name recognition when someone needs service
- Long-term customer lifetime value

## YOUR TASK
Vote YES or NO on implementing these improvements as standard protocol.

If YES, provide:
1. How to find contact names (tools, methods)
2. Suggested PDF audit structure with all services
3. Any modifications to Dan's suggestions

If NO, explain why not.

Format your response as:
- VOTE: YES or NO
- REASONING: [your explanation]
- IMPLEMENTATION: [specific steps if YES]
"""

def query_ai(name, url, headers, payload, extract_fn):
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=180)
        return {"ai": name, "vote": "PENDING", "raw": extract_fn(r.json())}
    except Exception as e:
        return {"ai": name, "vote": "ERROR", "raw": str(e)}

def query_claude():
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key: return {"ai": "Claude", "vote": "ERROR", "raw": "No API key"}
    return query_ai("Claude",
        "https://api.anthropic.com/v1/messages",
        {"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        {"model": "claude-sonnet-4-20250514", "max_tokens": 2000, "messages": [{"role": "user", "content": PROMPT}]},
        lambda d: d.get("content", [{}])[0].get("text", str(d))
    )

def query_grok():
    key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    if not key: return {"ai": "Grok", "vote": "ERROR", "raw": "No API key"}
    return query_ai("Grok",
        "https://api.x.ai/v1/chat/completions",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        {"model": "grok-3-latest", "messages": [{"role": "user", "content": PROMPT}]},
        lambda d: d.get("choices", [{}])[0].get("message", {}).get("content", str(d))
    )

def query_gemini():
    key = os.getenv("GEMINI_API_KEY")
    if not key: return {"ai": "Gemini", "vote": "ERROR", "raw": "No API key"}
    return query_ai("Gemini",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
        {"Content-Type": "application/json"},
        {"contents": [{"parts": [{"text": PROMPT}]}]},
        lambda d: d.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", str(d))
    )

def query_chatgpt():
    key = os.getenv("OPENAI_API_KEY")
    if not key: return {"ai": "ChatGPT", "vote": "ERROR", "raw": "No API key"}
    return query_ai("ChatGPT",
        "https://api.openai.com/v1/chat/completions",
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        {"model": "gpt-4o", "messages": [{"role": "user", "content": PROMPT}]},
        lambda d: d.get("choices", [{}])[0].get("message", {}).get("content", str(d))
    )

def extract_vote(raw):
    raw_upper = raw.upper()
    if "VOTE: YES" in raw_upper or "VOTE:YES" in raw_upper:
        return "YES"
    elif "VOTE: NO" in raw_upper or "VOTE:NO" in raw_upper:
        return "NO"
    return "UNCLEAR"

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    
    print("=" * 70)
    print("BOARD VOTE: Owner's Email Improvement Suggestions")
    print("=" * 70)
    
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(lambda f: f(), [query_claude, query_grok, query_gemini, query_chatgpt]))
    
    # Extract votes
    yes_votes = 0
    for r in results:
        r['vote'] = extract_vote(r['raw'])
        if r['vote'] == 'YES':
            yes_votes += 1
    
    print(f"\n{'='*70}")
    print("VOTE RESULTS")
    print('='*70)
    for r in results:
        print(f"{r['ai']}: {r['vote']}")
    
    print(f"\n{'='*70}")
    print(f"TOTAL: {yes_votes}/4 YES votes")
    if yes_votes >= 3:
        print("✅ APPROVED (3/4 threshold met)")
    else:
        print("❌ NOT APPROVED (need 3/4)")
    print('='*70)
    
    # Save results
    with open("board_vote_improvements.json", "w") as f:
        json.dump({"votes": results, "yes_count": yes_votes, "approved": yes_votes >= 3}, f, indent=2)
    
    print("\nDetailed responses saved to: board_vote_improvements.json")
