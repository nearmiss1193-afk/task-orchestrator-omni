#!/usr/bin/env python3
"""Board Review: Email Drafts Review by all AIs."""
import os
import json
import requests
from dotenv import load_dotenv

# Load secrets
load_dotenv(r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

# Read the email drafts
with open(r"C:\Users\nearm\.gemini\antigravity\brain\0b97dae9-c5c0-4924-8d97-793b59319985\email_drafts_board_review.md", "r") as f:
    EMAIL_DRAFTS = f.read()

PROMPT = f'''BOARD REVIEW: Email Drafts for Outreach Campaign

## YOUR ROLE
You are part of the AI Board reviewing cold outreach emails before they are sent to real businesses.

## TASK
Review the following 10 email drafts for:
1. **Accuracy** - Are the metrics cited (load times, SSL status) correct and not hallucinated?
2. **Professionalism** - Is the tone appropriate for business outreach?
3. **Compliance** - Does it avoid spam triggers and follow best practices?
4. **Effectiveness** - Will this email get opens/responses?
5. **Improvements** - What specific changes would make each email better?

## EMAIL DRAFTS TO REVIEW

{EMAIL_DRAFTS[:8000]}

---

## YOUR RESPONSE FORMAT

For each email (1-10), provide:
- **VERDICT**: APPROVE / NEEDS REVISION / REJECT
- **Issues Found**: List any problems
- **Suggested Fix**: Specific improvement

Then provide:
- **OVERALL VERDICT**: APPROVE ALL / REVISIONS NEEDED / REJECT BATCH
- **Summary**: 2-3 sentence overall assessment

Be concise but thorough. Focus on actionable feedback.
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
    print("=" * 70)
    print("BOARD REVIEW: Email Drafts")
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
    
    # Save results
    with open("board_email_review.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n")
    for r in results:
        print("=" * 70)
        print(f"=== {r['ai']} ===")
        print("=" * 70)
        text = r['raw']
        if len(text) > 3000:
            print(text[:3000] + "\n...[truncated]...")
        else:
            print(text)
        print()
    
    print("=" * 70)
    print("=== BOARD REVIEW COMPLETE ===")
    print("Results saved to: board_email_review.json")
    print("=" * 70)
