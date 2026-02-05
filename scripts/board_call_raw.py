#!/usr/bin/env python3
"""Board Protocol: Query all AIs for strategic decision."""
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''BOARD EMERGENCY: Security Incident and System Failures

## INCIDENT 1: EXPOSED API KEY (CRITICAL)
Google Cloud Trust & Safety detected a publicly accessible API key:
- Key: AIzaSyC5-5NI3HEyJiTscHYp-IKU6t2ebtKAtxQ (Gmail API)
- Location: https://github.com/nearmiss1193-afk/task-orchestrator-omni/blob/d5fc29114d68a89e2dcfad9974aa3a7ed823ff1b/knowledge_base/operational_memory.md
- Project: Empire-Email-Integration

**ROOT CAUSE**: operational_memory.md was pushed to GitHub with API keys in Section 13. 
We tried to exclude it from commits but it was already in git history.

**QUESTIONS**:
1. Should we regenerate this Gmail API key immediately?
2. How do we remove the key from git history (BFG Repo Cleaner or git filter-branch)?
3. Should we restrict the key's scope in Google Cloud Console?

## INCIDENT 2: GITHUB WORKFLOW FAILURES
Two workflows are failing:
1. "Deploy Empire Unified" - Some jobs not successful (commit 12a5ed2)
2. "System Watchdog" - All jobs have failed

**QUESTIONS**:
1. What's causing these failures?
2. Should we investigate before pushing more code?

## INCIDENT 3: SESSION SUMMARY EMAILS NOT ARRIVING
Dan reports he hasn't received any session summary emails despite Status 200 responses from GHL webhook.

**QUESTIONS**:
1. Is the GHL webhook URL correct?
2. Is there an issue with the email workflow in GHL?
3. How do we verify email delivery?

## BOARD RECOMMENDATIONS NEEDED

1. **IMMEDIATE**: What's the priority order for addressing these issues?
2. **API KEY**: Regenerate now or wait for board consensus?
3. **GIT HISTORY**: Best approach to remove secrets from history?
4. **WORKFLOWS**: Fix now or investigate first?
5. **EMAILS**: How to debug the delivery issue?

This is a security incident - please prioritize recommendations accordingly.
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
