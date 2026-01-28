
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
files = [
    "deploy_v2.py",
    "core/image_config.py",
    "workers/research.py",
    "workers/outreach.py",
    "workers/pulse_scheduler.py",
    "utils/error_handling.py",
    "api/webhooks.py"
]

FULL_CODE = ""
for fname in files:
    try:
        with open(fname, "r", encoding="utf-8") as f:
            FULL_CODE += f"\n\n# --- FILE: {fname} ---\n{f.read()}"
    except Exception as e:
        print(f"Error reading {fname}: {e}")

print(f"Loaded {len(FULL_CODE)} bytes of code.")

def run_audit():
    report = f"# 🕵️ FINAL MODULAR REFACTOR AUDIT\n\n{LIMITS}\n\n"
    
    # 1. GROK
    if GROK_KEY:
        print("Querying Grok...")
        try:
            res = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROK_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "grok-3", 
                    "messages": [{"role": "user", "content": f"{LIMITS}\nAUDIT THIS CODE FOR ARCHITECTURE AND LIMITS:\n{FULL_CODE[:55000]}"}]
                },
                timeout=60
            )
            data = res.json()
            if 'choices' in data:
                report += f"## 🌌 GROK ANALYSIS\n{data['choices'][0]['message']['content']}\n\n"
            else:
                report += f"## 🌌 GROK ERROR\n{data}\n\n"
        except Exception as e:
            report += f"## 🌌 GROK EXCEPTION\n{e}\n\n"
    else:
        report += "## 🌌 GROK SKIPPED (No Key)\n\n"

    # 2. GEMINI
    if GEMINI_KEY:
        print("Querying Gemini...")
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(f"{LIMITS}\nAUDIT THIS CODE:\n{FULL_CODE[:30000]}")
            report += f"## 🤖 GEMINI ANALYSIS\n{res.text}\n\n"
        except Exception as e:
             report += f"## 🤖 GEMINI EXCEPTION\n{e}\n\n"
    else:
        report += "## 🤖 GEMINI SKIPPED (No Key)\n\n"

    # 3. SAVE
    with open("final_audit.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("✅ Audit Complete. Saved to final_audit.md")

if __name__ == "__main__":
    run_audit()
