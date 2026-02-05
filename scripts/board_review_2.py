#!/usr/bin/env python3
"""Board Review #2: Revised Email Drafts."""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

# Read the revised email drafts
with open(r"C:\Users\nearm\.gemini\antigravity\brain\0b97dae9-c5c0-4924-8d97-793b59319985\email_drafts_batch1_revised.md", "r", encoding="utf-8") as f:
    EMAIL_DRAFTS = f.read()

PROMPT = """BOARD REVIEW #2: Revised Email Drafts

## CONTEXT
These are REVISED emails based on your previous feedback. All 10 have been updated.

## CHANGES MADE (per Board feedback):
1. Replaced ALL emojis with text indicators (CRITICAL, WARNING, GOOD, EXCELLENT)
2. Completed ALL truncated emails
3. Added clear CTAs to every email
4. Fixed 403 vs SSL confusion (Vanguard email)
5. Explained AI Intake trial benefits in each email
6. Added personalization and local focus
7. Softened alarmist tone

## YOUR TASK
Review ALL 10 emails again and determine if revisions are acceptable.

For each email, provide:
- **VERDICT**: APPROVE / NEEDS REVISION
- **Comments**: Any remaining concerns (or "None - approved")

Then provide:
- **OVERALL VERDICT**: ALL APPROVED / STILL NEEDS WORK
- **Summary**: 1-2 sentences

Be strict but fair. These must be professional, accurate, and effective.

---

## REVISED EMAIL DRAFTS

""" + EMAIL_DRAFTS[:12000]

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
    api_key = os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")
    if not api_key:
        return {"ai": "Grok", "raw": "ERROR: No GROK_API_KEY"}
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
    print("=" * 70)
    print("BOARD REVIEW #2: Revised Email Drafts")
    print("Querying Claude, Grok, Gemini, ChatGPT...")
    print("=" * 70)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(query_claude),
            executor.submit(query_grok),
            executor.submit(query_gemini),
            executor.submit(query_chatgpt),
        ]
        results = [f.result() for f in futures]
    
    with open("board_review_2.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n")
    for r in results:
        print("=" * 70)
        print(f"=== {r['ai']} ===")
        print("=" * 70)
        text = r['raw']
        if len(text) > 2500:
            print(text[:2500] + "\n...[truncated]...")
        else:
            print(text)
        print()
    
    print("=" * 70)
    print("=== BOARD REVIEW #2 COMPLETE ===")
    print("Results saved to: board_review_2.json")
    print("=" * 70)
