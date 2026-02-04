"""
WEBSITE BOARD MEETING SCRIPT
============================
Calls Claude, Grok, Gemini, and ChatGPT APIs to get REAL multi-AI analysis
of the aiserviceco.com website and recommendations for fixing it.

Usage: python scripts/website_board_meeting.py
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# === CONFIGURATION ===
SOVEREIGN_STATE_URL = "https://nearmiss1193-afk--ghl-omni-automation-sovereign-state.modal.run"
SOVEREIGN_TOKEN = "sov-audit-2026-ghost"
WEBSITE_URL = "https://www.aiserviceco.com"

WEBSITE_PROMPT = """
You are a senior web development consultant reviewing a client's website.

**Website**: aiserviceco.com (AI Service Agency selling AI Voice Agents)

**Current System State**:
{sovereign_state}

**Known Issues** (from session context):
1. Contact section may still have old Calendly/formsubmit.co instead of GHL embeds
2. Sarah Voice Widget - uncertain if showing minimalist icon or full white text box
3. Last outreach was 5 days ago (Jan 30)
4. Embed codes are locked in Supabase but may not be deployed to site

**Your Task**:
Provide a brief, actionable assessment (under 150 words):

1. **Critical Fix** (priority #1 to address immediately)
2. **Quick Wins** (1-2 easy improvements)
3. **Recommended Action** (next step to take)

Be specific and practical. No fluff.
"""

def get_sovereign_state():
    """Fetch real data from the Sovereign State endpoint."""
    try:
        r = requests.get(f"{SOVEREIGN_STATE_URL}?token={SOVEREIGN_TOKEN}", timeout=30)
        return r.json() if r.status_code == 200 else {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def call_claude(prompt):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"ai": "Claude", "response": "❌ ANTHROPIC_API_KEY not found"}
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 400, "messages": [{"role": "user", "content": prompt}]},
            timeout=60
        )
        data = r.json()
        return {"ai": "Claude", "response": data.get("content", [{}])[0].get("text", str(data))}
    except Exception as e:
        return {"ai": "Claude", "response": f"❌ Error: {str(e)}"}

def call_grok(prompt):
    api_key = os.environ.get("GROK_API_KEY")
    if not api_key:
        return {"ai": "Grok", "response": "❌ GROK_API_KEY not found"}
    try:
        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "grok-3", "messages": [{"role": "user", "content": prompt}], "max_tokens": 400},
            timeout=60
        )
        data = r.json()
        return {"ai": "Grok", "response": data.get("choices", [{}])[0].get("message", {}).get("content", str(data))}
    except Exception as e:
        return {"ai": "Grok", "response": f"❌ Error: {str(e)}"}

def call_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"ai": "Gemini", "response": "❌ GEMINI_API_KEY not found"}
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=60
        )
        data = r.json()
        return {"ai": "Gemini", "response": data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", str(data))}
    except Exception as e:
        return {"ai": "Gemini", "response": f"❌ Error: {str(e)}"}

def call_chatgpt(prompt):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"ai": "ChatGPT", "response": "❌ OPENAI_API_KEY not found"}
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "max_tokens": 400},
            timeout=60
        )
        data = r.json()
        return {"ai": "ChatGPT", "response": data.get("choices", [{}])[0].get("message", {}).get("content", str(data))}
    except Exception as e:
        return {"ai": "ChatGPT", "response": f"❌ Error: {str(e)}"}

def run_website_board():
    print("=" * 70)
    print("🏛️ WEBSITE BOARD MEETING: aiserviceco.com")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # Step 1: Get real system state
    print("\n📡 Fetching Sovereign State...")
    state = get_sovereign_state()
    print(f"System Mode: {state.get('system_mode', 'unknown')}")
    
    # Step 2: Build website-focused prompt
    prompt = WEBSITE_PROMPT.format(sovereign_state=json.dumps(state, indent=2))
    
    # Step 3: Call each AI
    print("\n🤖 Convening Board Meeting...")
    board_responses = []
    
    for caller, name in [(call_claude, "Claude"), (call_grok, "Grok"), (call_gemini, "Gemini"), (call_chatgpt, "ChatGPT")]:
        print(f"  → {name} is analyzing...")
        response = caller(prompt)
        board_responses.append(response)
        print(f"    ✅ {name} submitted recommendation")
    
    # Step 4: Print results
    print("\n" + "=" * 70)
    print("📊 BOARD RECOMMENDATIONS")
    print("=" * 70)
    
    for resp in board_responses:
        print(f"\n### {resp['ai'].upper()}")
        print("-" * 50)
        print(resp['response'])
    
    # Step 5: Save report
    report = {
        "meeting_type": "Website Analysis",
        "website": "aiserviceco.com",
        "timestamp": datetime.now().isoformat(),
        "sovereign_state": state,
        "board_recommendations": board_responses
    }
    
    with open("website_board_meeting.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ BOARD MEETING COMPLETE – Saved to website_board_meeting.json")
    print("=" * 70)

if __name__ == "__main__":
    run_website_board()
