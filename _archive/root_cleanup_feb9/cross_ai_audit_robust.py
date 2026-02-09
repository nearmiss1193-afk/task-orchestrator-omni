
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# KEYS
CLAUDE_KEY = os.environ.get("ANTHROPIC_API_KEY")
GROK_KEY = os.environ.get("GROK_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# LIMITS (User requested)
LIMITS = """
CRITICAL CONSTRAINTS:
- MODAL: Free Tier (Max 5 Crons, limited concurrency).
- SUPABASE: Pro Plan ($25/mo, 100k writes/mo).
- GHL: $99/mo Plan (API limits apply).
- VAPI: Pay-As-You-Go (Minimize unnecessary polling).
"""

# LOAD CODE

source_files = [
    "deploy.py",
    "core/image_config.py",
    "workers/research.py",
    "workers/outreach.py",
    "workers/pulse_scheduler.py",
    "api/webhooks.py"
]

FAILURE_CONTEXT = """
The user triggered a simulation to +13529368152 (Dan).
1. Vapi reported 201 Created but the call ended with 'call.start.error-get-transport'.
2. GHL reported 200 OK for SMS but the user says it never arrived and the dashboard shows 'DND enabled' for a similar contact.
3. The Vapi Phone ID used was for a Twilio-imported number (+18632608351).
"""

def generate_prompt(code_context):
    return f"""
    You are part of a high-level engineering audit panel. 
    
    CODE CONTEXT:
    {code_context}
    
    FAILURE CONTEXT:
    {FAILURE_CONTEXT}
    
    TASK:
    1. Identify why the outbound call failed (Look at Vapi Phone ID ee668638-38f0-4984-81ae-e2fd5d83084b).
    2. Identify why the SMS might be blocked (Look at GHL DND flags).
    3. Confirm if Rule #1 was violated (reporting success without proof).
    4. Provide the exact fix.
    """

FULL_CODE = ""
for fname in source_files:
    try:
        with open(fname, "r", encoding="utf-8") as f:
            FULL_CODE += f"\n\n# --- FILE: {fname} ---\n{f.read()}"
    except Exception as e:
        print(f"Error reading {fname}: {e}")

print(f"Loaded {len(FULL_CODE)} bytes of code.")


# OPENAI
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

def query_grok(prompt):
    res = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROK_KEY}", "Content-Type": "application/json"},
        json={"model": "grok-3", "messages": [{"role": "user", "content": prompt}]},
        timeout=60
    )
    return res.json()['choices'][0]['message']['content'] if 'choices' in res.json() else str(res.json())

def query_openai(prompt):
    res = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
        json={"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}]},
        timeout=60
    )
    return res.json()['choices'][0]['message']['content'] if 'choices' in res.json() else str(res.json())

def query_claude(prompt):
    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": CLAUDE_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=60
    )
    return res.json()['content'][0]['text'] if 'content' in res.json() else str(res.json())

def run_audit():
    prompt = generate_prompt(FULL_CODE[:40000]) # Stay within context limits
    report = f"# 🕵️ FINAL MODULAR REFACTOR AUDIT (DIVERGENT PANEL)\n\n{LIMITS}\n\n"
    
    # 1. GROK
    if GROK_KEY:
        print("Querying Grok-3...")
        try: report += f"## 🌌 GROK-3 ANALYSIS\n{query_grok(prompt)}\n\n"
        except Exception as e: report += f"## 🌌 GROK EXCEPTION\n{e}\n\n"
    
    # 2. OPENAI
    if OPENAI_KEY:
        print("Querying GPT-4o...")
        try: report += f"## 🤖 OPENAI ANALYSIS\n{query_openai(prompt)}\n\n"
        except Exception as e: report += f"## 🤖 OPENAI EXCEPTION\n{e}\n\n"
        
    # 3. CLAUDE
    if CLAUDE_KEY:
        print("Querying Claude 3.5...")
        try: report += f"## 🎭 CLAUDE ANALYSIS\n{query_claude(prompt)}\n\n"
        except Exception as e: report += f"## 🎭 CLAUDE EXCEPTION\n{e}\n\n"

    # SAVE
    with open("final_audit.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ Full Audit Complete. Saved to final_audit.md")

if __name__ == "__main__":
    run_audit()
