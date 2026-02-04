"""
CROSS-AI BOARD AUDIT SCRIPT
============================
Calls Claude, Grok, Gemini, and ChatGPT APIs to get REAL multi-AI analysis
of the Sovereign State endpoint.

Usage: python scripts/cross_ai_board.py

Requires API keys in .env:
- ANTHROPIC_API_KEY (Claude)
- GROK_API_KEY (Grok/xAI)
- GEMINI_API_KEY (Google)
- OPENAI_API_KEY (ChatGPT)

Author: Antigravity v5.5
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

AUDIT_PROMPT = """
You are a technical auditor reviewing a system's health status. Analyze this JSON and provide a brief assessment:

1. Is the system healthy? (Yes/No + reason)
2. Any red flags or issues?
3. One recommendation for improvement.

Keep your response under 100 words.

SYSTEM STATE:
{state_json}
"""

# === API CALLERS ===

def get_sovereign_state():
    """Fetch real data from the Sovereign State endpoint."""
    try:
        r = requests.get(f"{SOVEREIGN_STATE_URL}?token={SOVEREIGN_TOKEN}", timeout=30)
        return r.json() if r.status_code == 200 else {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def call_claude(prompt):
    """Call Claude/Anthropic API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"ai": "Claude", "response": "❌ ANTHROPIC_API_KEY not found"}
    
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        data = r.json()
        return {"ai": "Claude", "response": data.get("content", [{}])[0].get("text", str(data))}
    except Exception as e:
        return {"ai": "Claude", "response": f"❌ Error: {str(e)}"}

def call_grok(prompt):
    """Call Grok/xAI API."""
    api_key = os.environ.get("GROK_API_KEY")
    if not api_key:
        return {"ai": "Grok", "response": "❌ GROK_API_KEY not found"}
    
    try:
        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "grok-3",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300
            },
            timeout=30
        )
        data = r.json()
        return {"ai": "Grok", "response": data.get("choices", [{}])[0].get("message", {}).get("content", str(data))}
    except Exception as e:
        return {"ai": "Grok", "response": f"❌ Error: {str(e)}"}

def call_gemini(prompt):
    """Call Google Gemini API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"ai": "Gemini", "response": "❌ GEMINI_API_KEY not found"}
    
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}]
            },
            timeout=30
        )
        data = r.json()
        return {"ai": "Gemini", "response": data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", str(data))}
    except Exception as e:
        return {"ai": "Gemini", "response": f"❌ Error: {str(e)}"}

def call_chatgpt(prompt):
    """Call OpenAI ChatGPT API."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"ai": "ChatGPT", "response": "❌ OPENAI_API_KEY not found"}
    
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300
            },
            timeout=30
        )
        data = r.json()
        return {"ai": "ChatGPT", "response": data.get("choices", [{}])[0].get("message", {}).get("content", str(data))}
    except Exception as e:
        return {"ai": "ChatGPT", "response": f"❌ Error: {str(e)}"}

# === MAIN AUDIT ===

def run_board_audit():
    """Run the full cross-AI board audit."""
    print("=" * 60)
    print("🏛️ CROSS-AI BOARD AUDIT")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Step 1: Get real system state
    print("\n📡 Fetching Sovereign State...")
    state = get_sovereign_state()
    print(f"System Mode: {state.get('system_mode', 'unknown')}")
    print(f"Health: {state.get('health', {})}")
    
    if "error" in state:
        print(f"❌ Failed to fetch state: {state['error']}")
        return
    
    # Step 2: Build prompt with real data
    prompt = AUDIT_PROMPT.format(state_json=json.dumps(state, indent=2))
    
    # Step 3: Call each AI
    print("\n🤖 Polling Board Members...")
    board_responses = []
    
    for caller, name in [(call_claude, "Claude"), (call_grok, "Grok"), (call_gemini, "Gemini"), (call_chatgpt, "ChatGPT")]:
        print(f"  → Calling {name}...")
        response = caller(prompt)
        board_responses.append(response)
        print(f"    ✅ {name} responded")
    
    # Step 4: Print results
    print("\n" + "=" * 60)
    print("📊 BOARD RESPONSES")
    print("=" * 60)
    
    for resp in board_responses:
        print(f"\n### {resp['ai']}")
        print("-" * 40)
        print(resp['response'])
    
    # Step 5: Save to file
    report = {
        "audit_timestamp": datetime.now().isoformat(),
        "sovereign_state": state,
        "board_responses": board_responses
    }
    
    with open("board_audit_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ AUDIT COMPLETE – Saved to board_audit_report.json")
    print("=" * 60)

if __name__ == "__main__":
    run_board_audit()
