#!/usr/bin/env python3
"""Board Protocol: Query all AIs for strategic decision."""
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''SESSION REVIEW: Process Improvement Analysis (Feb 5, 2026)

## CONTEXT
Today's session revealed several inefficiencies that caused delays. The user (Dan) expressed frustration that tasks which were completed successfully earlier in the session couldn't be replicated later without wasting time.

## KEY ISSUES IDENTIFIED

### Issue 1: Email Sending Capability Lost
- Earlier in session: Successfully sent emails via reliable_email.py
- Later in session: Agent tried Gmail (wrong approach), had PowerShell syntax errors
- User feedback: "I hate to have to spend an hour each day to have you find a way to do something that you did yesterday"

### Issue 2: Batch Count Confusion
- User originally asked for 10 emails
- Agent only prepared 6 emails initially
- User had to correct this mid-task

### Issue 3: Approval Email Never Sent
- Gmail approach failed (needs app password)
- Multiline string caused PowerShell syntax error
- Finally used reliable_email.py (the correct method)

## SESSION TIMELINE

1. User requested 10 emails for owner approval
2. Agent researched and verified email addresses
3. Agent drafted emails using approved template
4. Board review completed (4/4 approval for Batch 1)
5. Approval email failed multiple times before success
6. User had to remind agent about correct email count
7. User requested process improvement review

## QUESTIONS FOR BOARD

1. **How can we ensure learned capabilities are not forgotten mid-session?**
   - Should there be a "working commands" log?
   - Should operational_memory.md be updated more aggressively?

2. **What protocols should be added to prevent these specific issues?**
   - Pre-task checklist?
   - Mandatory re-read of operational_memory before each major action?

3. **How can we improve user experience?**
   - Faster execution with fewer errors
   - Better confirmation of completed actions
   - Proactive communication

4. **What documentation changes are needed?**
   - operational_memory.md updates?
   - New workflow files?
   - Quick reference cards?

Please provide:
- Specific recommendations
- Priority ranking (High/Medium/Low)
- Implementation suggestions
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
    import sys
    from concurrent.futures import ThreadPoolExecutor
    
    # Accept prompt from command line if provided
    if len(sys.argv) > 1:
        PROMPT = sys.argv[1]
        print(f">> {PROMPT[:200]}..." if len(PROMPT) > 200 else f">> {PROMPT}")
    
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
