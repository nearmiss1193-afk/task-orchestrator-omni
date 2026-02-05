#!/usr/bin/env python3
"""Board Protocol: Query all AIs for strategic decision."""
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''BOARD QUERY: Design a "Street Light" Audit Email Format for B2B Prospecting

## Context
AI Service Co sends personalized prospecting emails that include audit results (PageSpeed scores, GHL/CRM audits, website analysis). The owner wants a "traffic light" format to present findings:

- 🔴 **RED** = CRITICAL - Things they MUST fix immediately (urgent problems)
- 🟡 **YELLOW** = WARNING - Things they SHOULD fix (moderate issues)  
- 🟢 **GREEN** = GOOD - Things that are working well (positives)

**Goal:** Make the audit results easy to understand at a 5th grade reading level. Visual. Scannable. Drives action.

**Current Audit Data Available:**
- PageSpeed scores (Performance, Accessibility, Best Practices, SEO)
- Website analysis (loading speed, mobile-friendly, etc.)
- GHL/CRM gaps (missing automations, lead tracking issues)

## Questions for the Board

1. **What's the ideal structure for a traffic light audit email?**
   - How should RED/YELLOW/GREEN sections be organized?
   - What's the right balance of findings per category?
   - Should GREEN come first (build rapport) or RED (create urgency)?

2. **What specific metrics map to each color?**
   - PageSpeed: What scores = RED vs YELLOW vs GREEN?
   - Other website metrics: What thresholds matter?
   - How do you communicate CRM/GHL gaps in this format?

3. **How should the email be worded?**
   - Bullet points vs sentences?
   - Technical jargon vs plain English?
   - Example text for each color section?

4. **What psychological principles make this effective?**
   - How does the color coding drive action?
   - What order maximizes response rates?

5. **Please provide a COMPLETE EMAIL TEMPLATE example**
   - Subject line
   - Opening line (personalized)
   - The traffic light audit section
   - Call-to-action
   - Signature

The template should be at a 5th grade reading level. Make it visual, simple, and action-driving.
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
