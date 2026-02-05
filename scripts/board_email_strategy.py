#!/usr/bin/env python3
"""Board Protocol: Query AIs for GHL Email Strategy Decision."""
import os
import json
import requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = '''BOARD STRATEGIC DECISION: GHL Email Automation vs Alternatives

## SITUATION
I (Antigravity AI) am trying to send outreach emails for AI Service Co.
Currently facing an email deliverability problem:

### CURRENT STATE:
1. **GHL Webhooks**: Return HTTP 200 "Success" but emails NOT delivered
   - Webhook URL accepts requests
   - But GHL workflow on the other end doesn't actually send the email
   - GHL API direct access: DOESN'T WORK (private integration only - verified)
   
2. **Resend API**: Working but Dan says "always goes to spam folders"
   - API works, emails send successfully
   - But inbox placement is poor

3. **Browser Automation**: Playwright script failed
   - GHL login timeout issues
   - 2FA may be blocking automated access

### GHL CREDENTIALS (Available):
- Email: nearmiss1193@gmail.com
- Password: Inez11752990@
- Location ID: RnK4OjX0oDcqtWw0VyLr

### THE CORE QUESTION:
Should I invest time learning to properly automate GHL email sending (browser automation, fixing workflows), OR is there a better alternative approach?

---

## BOARD QUESTIONS:

### 1. GHL VALUE ASSESSMENT
- Is GHL email worth fixing? What's the deliverability advantage over Resend?
- Does GHL provide better inbox placement for cold outreach?

### 2. TECHNICAL FEASIBILITY
- Can GHL browser automation work reliably for email sending?
- Is there a way to fix the GHL webhook → email workflow?
- What about using GHL's native campaigns/automation features?

### 3. ALTERNATIVE APPROACHES
- What are the best cold email sending options in 2026?
- Should we consider: Instantly, Lemlist, Apollo, Smartlead, Woodpecker?
- What about sending through Gmail directly with proper warm-up?

### 4. TIME vs BENEFIT ANALYSIS
- How much time should be invested in fixing GHL email?
- Is it worth learning GHL deeply or should we use simpler tools?

### 5. DELIVERABILITY BEST PRACTICES
- What actually determines inbox vs spam placement?
- What configuration would give us best cold email deliverability?

### 6. RECOMMENDED STRATEGY
Based on all factors, what is the BEST path forward for autonomous outreach email sending that:
- Actually reaches prospect inboxes
- Can be automated without manual intervention
- Is reliable and scalable

---

## EXPECTED OUTPUT:
1. Clear recommendation: GHL vs Alternative
2. If GHL: Specific steps to fix the workflow
3. If Alternative: Recommended tool and setup
4. Deliverability tips regardless of choice
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

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    print("=" * 60)
    print("BOARD QUERY: GHL Email Strategy Decision")
    print("=" * 60)
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(query_claude),
            executor.submit(query_grok),
            executor.submit(query_gemini),
        ]
        results = [f.result() for f in futures]
    
    output_file = "board_email_strategy.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    print("\n" + "=" * 60)
    
    for r in results:
        print(f"\n=== {r['ai']} ===")
        print(r['raw'][:3000] + "..." if len(r['raw']) > 3000 else r['raw'])
        print("-" * 60)
    
    print("\n=== BOARD CONSULTATION COMPLETE ===")
