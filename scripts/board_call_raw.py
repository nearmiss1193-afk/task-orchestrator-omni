#!/usr/bin/env python3
"""Board Protocol: Query all AIs for strategic decision."""
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''BOARD REVIEW: Email Drafts for Outreach Campaign

## CONTEXT
Dan has approved 10 email drafts for his outreach campaign. Before sending to Dan for final review, the board must achieve 3/4 (75%) consensus on whether these emails are ready.

## EMAIL TEMPLATE FORMAT
All 10 emails follow the "bfisher audit format" with:
1. Traffic Light table (CRITICAL/WARNING/OPPORTUNITY)
2. Industry-specific language
3. "Free fix" local guarantee
4. 14-day trial offer
5. "Follow up in an hour" CTA

## SAMPLE EMAIL (Representative of all 10)

Subject: [Business Name] - Digital Performance Audit Results

Dear [Name/Business Owner],

I am a local digital strategist here in Lakeland, and I've conducted a brief health audit of [Business]'s online presence.

AREA                 STATUS              THE RISK TO THE BUSINESS
---------------------------------------------------------------------------
Search Visibility    CRITICAL (RED)      The site may be failing Google's Core Web Vitals...
Legal Compliance     WARNING (YELLOW)    The site may be missing a dedicated Privacy Policy...
Lead Efficiency      OPPORTUNITY         Your team may be manually filtering every inquiry...

THE SOLUTION: I specialize in helping [industry] businesses bridge these gaps. 14-day trial offer...

MY LOCAL GUARANTEE: Because I am a local Lakeland resident, I would like to fix your Search Visibility for free this week...

I will follow up with your office in an hour to see if you have any questions.

Best regards,
Daniel Coffman
352-936-8152
Owner, AI Service Co

## 10 BUSINESSES TARGETED
1. Lakeland Roofing Company (roofing)
2. All Pro Roofing (roofing)
3. Precision Roofing Lakeland (roofing)
4. Scott's Air Conditioning - Contact: Craig Fortin (HVAC)
5. Air Pros USA - Contact: Allisa Sommers (HVAC)
6. Lakeland Air Conditioning (HVAC)
7. Viper Auto Care (auto)
8. Honest 1 Auto Care Lakeland (auto)
9. Premium Auto Repair (auto)
10. ABC Plumbing Lakeland (plumbing)

## BOARD QUESTIONS

1. **FORMAT**: Does the Traffic Light table format effectively communicate value? Any improvements?

2. **CLAIMS**: Are there any legal/ethical concerns with:
   - Saying the site "may be failing" Google standards?
   - Offering a "free fix" for search visibility?
   - Mentioning the "Florida Digital Bill of Rights"?

3. **CTA**: Is "I will follow up in an hour" too aggressive? Should it be softened?

4. **PERSONALIZATION**: 4 emails have contact names (Craig, Allisa), 6 say "Dear Business Owner". Is this balance acceptable?

5. **APPROVAL**: Do you approve sending these emails to Dan for final review?

Please vote: APPROVE / REJECT with specific feedback.
3/4 consensus required to proceed.
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
