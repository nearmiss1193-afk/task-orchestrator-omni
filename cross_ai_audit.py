
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

CLAUDE_KEY = os.environ.get("ANTHROPIC_API_KEY")
GROK_KEY = os.environ.get("GROK_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

LIMITS_CONTEXT = """
SYSTEM CONSTRAINTS & LIMITS:
1. MODAL: Free Tier / Starter (Max 5 Crons, limited concurrency).
2. SUPABASE: Pro Plan (Good limits, but don't abuse connections).
3. GHL: $99/mo Plan (Standard limits).
4. VAPI: Pay As You Go (Cost sensitive).
"""

CODE_CONTEXT = ""
files_to_read = [
    "deploy_v2.py",
    "core/image_config.py",
    "workers/research.py",
    "workers/outreach.py",
    "workers/pulse_scheduler.py",
    "utils/error_handling.py",
    "api/webhooks.py"
]

for fname in files_to_read:
    try:
        with open(fname, "r", encoding="utf-8") as f:
            CODE_CONTEXT += f"\n\n# --- FILE: {fname} ---\n{f.read()}"
    except Exception as e:
        print(f"Skipping {fname}: {e}")

def audit_with_claude(code):
    if not CLAUDE_KEY: return "Claude Key Missing"
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": CLAUDE_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    candidates = ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229"]
    for model in candidates:
        try:
            data = {"model": model, "max_tokens": 4096, "messages": [{"role": "user", "content": f"{LIMITS_CONTEXT}\nAUDIT THIS REFACTORED CODE:\n{code[:80000]}"}]}
            res = requests.post(url, headers=headers, json=data).json()
            if 'content' in res: return res['content'][0]['text']
        except: continue
    return "Claude Failed"

def audit_with_grok(code):
    if not GROK_KEY: return "Grok Key Missing"
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROK_KEY}", "Content-Type": "application/json"}
    try:
        data = {"model": "grok-beta", "messages": [{"role": "user", "content": f"{LIMITS_CONTEXT}\nAUDIT THIS REFACTORED CODE:\n{code[:50000]}"}]}
        res = requests.post(url, headers=headers, json=data).json()
        if 'choices' in res: return res['choices'][0]['message']['content']
    except: pass
    return "Grok Failed"

def audit_with_gemini(code):
    if not GEMINI_KEY: return "Gemini Key Missing"
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_KEY)
    candidates = ['gemini-1.5-pro', 'gemini-1.5-flash']
    for m in candidates:
        try:
            model = genai.GenerativeModel(m)
            res = model.generate_content(f"{LIMITS_CONTEXT}\nAUDIT THIS CODE:\n{code[:30000]}")
            return res.text
        except: continue
    return "Gemini Failed"

def audit_with_openai(code):
    if not OPENAI_KEY: return "OpenAI Key Missing"
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    try:
        data = {"model": "gpt-4o", "messages": [{"role": "user", "content": f"{LIMITS_CONTEXT}\nAUDIT THIS REFACTORED CODE:\n{code[:50000]}"}]}
        res = requests.post(url, headers=headers, json=data).json()
        if 'choices' in res: return res['choices'][0]['message']['content']
        else: return str(res)
    except Exception as e: return f"OpenAI Failed: {e}"

if __name__ == "__main__":
    print(f"Read {len(CODE_CONTEXT)} bytes of code.")
    
    report = f"# 🕵️ FINAL REFACTOR AUDIT\n\n"
    
    print("Asking Gemini...")
    report += f"## GEMINI\n{audit_with_gemini(CODE_CONTEXT)}\n\n"
    
    print("Asking Claude...")
    report += f"## CLAUDE\n{audit_with_claude(CODE_CONTEXT)}\n\n"
    
    print("Asking Grok...")
    report += f"## GROK\n{audit_with_grok(CODE_CONTEXT)}\n\n"
    
    print("Asking OpenAI...")
    report += f"## OPENAI\n{audit_with_openai(CODE_CONTEXT)}\n\n"
    
    with open("final_audit.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("Done! Saved to final_audit.md")
