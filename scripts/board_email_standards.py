#!/usr/bin/env python3
"""Board Research: Define Email Outreach Standards."""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(r"c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

PROMPT = """BOARD RESEARCH REQUEST: Define Cold Outreach Email Standards

## CONTEXT
Dan (owner of AI Service Co) is sending cold outreach emails to local service businesses (HVAC, Plumbing, Roofing, Electrical) in Lakeland, FL. 

He has provided examples of the format he wants (bfisher format):
1. Traffic light table with colored indicators (🔴 CRITICAL, 🟡 WARNING, 🟢 OPPORTUNITY)
2. Attached PDF audit report with:
   - Executive Summary
   - Critical Findings
   - Proposed Solutions
3. Screenshots attached (unclear what type)

## THE QUESTION
We need to define comprehensive standards for:
1. What screenshots should we attach? (PageSpeed results? Website homepage? Both? Mobile view?)
2. What should the PDF audit report contain? (What sections, what metrics, how detailed?)
3. What is the optimal email body format for local service businesses?
4. What attachments maximize open rates without triggering spam filters?

## YOUR TASK
Research and provide recommendations on:

### 1. SCREENSHOTS TO INCLUDE
- What specific screenshots should be attached?
- PageSpeed Insights results?
- Google Lighthouse audit?
- Website mobile view?
- GTmetrix or similar tools?
- What format (PNG, PDF)?

### 2. PDF AUDIT REPORT STRUCTURE
- What sections should it contain?
- How detailed should findings be?
- What professional format works best?
- Should it look "polished" or "rough" (some say rough = more authentic)?

### 3. EMAIL BODY BEST PRACTICES
- Traffic light table: HTML or plain text?
- Length: Short and punchy or detailed?
- Personalization elements?
- Call-to-action placement?

### 4. ATTACHMENT STRATEGY
- How many attachments before spam triggers?
- Total file size limits?
- Inline images vs attachments?

### 5. COLD EMAIL COMPLIANCE
- CAN-SPAM requirements
- Unsubscribe requirements for cold emails
- Legal considerations

## EXPECTED OUTPUT
Provide specific, actionable recommendations that we can implement immediately. Be concrete about what files to create and attach.

Format your response as a clear standard we can follow.
"""

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
                "max_tokens": 3000,
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
        return {"ai": "Grok", "raw": "ERROR: No GROK_API_KEY"}
    try:
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "grok-3-latest", "messages": [{"role": "user", "content": PROMPT}]},
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

def query_chatgpt():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"ai": "ChatGPT", "raw": "ERROR: No OPENAI_API_KEY"}
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-4o", "messages": [{"role": "user", "content": PROMPT}]},
            timeout=180,
        )
        data = response.json()
        return {"ai": "ChatGPT", "raw": data.get("choices", [{}])[0].get("message", {}).get("content", str(data))}
    except Exception as e:
        return {"ai": "ChatGPT", "raw": f"ERROR: {e}"}

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    print("=" * 70)
    print("BOARD RESEARCH: Email Outreach Standards")
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
    
    with open("board_email_standards.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n")
    for r in results:
        print("=" * 70)
        print(f"=== {r['ai']} ===")
        print("=" * 70)
        print(r['raw'][:4000] if len(r['raw']) > 4000 else r['raw'])
        print()
    
    print("=" * 70)
    print("Results saved to: board_email_standards.json")
    print("=" * 70)
