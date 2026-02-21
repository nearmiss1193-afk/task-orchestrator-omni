"""
SEO BOARD CALL - Multi-AI Brainstorming Session for LakelandFinds & AIServiceCo
"""
import requests, os, json, time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
load_dotenv('.env.local')

RECEIPTS = []
BOARD_RESPONSES = {}

def log_receipt(board_member, endpoint, status_code, request_body_preview, response_preview):
    receipt = {
        "timestamp": datetime.now().isoformat(),
        "board_member": board_member,
        "endpoint": endpoint,
        "http_status": status_code,
        "request_preview": request_body_preview[:200],
        "response_preview": response_preview[:500]
    }
    RECEIPTS.append(receipt)
    return receipt

BOARD_PROMPT = """You are on the AI Board of Directors. The CEO wants to dominate search rankings for two domains:
1. AIServiceCo.com (B2B SaaS / AI Automation Agency)
2. LakelandFinds.com (Local Business Directory for Lakeland, FL)

He received some advice from Perplexity but wants the Board's creative consensus. 

Provide a highly actionable, structured SEO game plan specifically addressing:
1. PAGE STRATEGY: Exactly what types of pages/programmatic SEO assets should we build?
2. LINK STRATEGY: How do we build high-authority links in 2026 for these specific niches?
3. CREATIVE / OUT-OF-THE-BOX: What are unconventional SEO strategies we can execute that competitors aren't doing?

Keep it under 400 words. Be specific, dense with value, and highly actionable."""

# === GROK ===
print("=" * 60)
print("CALLING GROK (xAI)...")
grok_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
if grok_key:
    try:
        grok_body = {
            "messages": [
                {"role": "system", "content": "You are Grok, the Intelligence Officer on the AI board. Your role is deep technical analysis and unconventional growth hacks."},
                {"role": "user", "content": BOARD_PROMPT}
            ],
            "model": "grok-3-mini",
            "temperature": 0.4,
            "max_tokens": 800
        }
        t0 = time.time()
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"},
            json=grok_body,
            timeout=60
        )
        if resp.status_code == 200:
            BOARD_RESPONSES["GROK"] = resp.json()['choices'][0]['message']['content']
            print(f"✅ Grok responded ({round(time.time() - t0, 2)}s)")
        else:
            BOARD_RESPONSES["GROK"] = f"ERROR {resp.status_code}"
    except Exception as e:
        BOARD_RESPONSES["GROK"] = f"EXCEPTION: {e}"

# === OPENAI ===
print("=" * 60)
print("CALLING CHATGPT (OpenAI)...")
openai_key = os.environ.get("OPENAI_API_KEY")
if openai_key:
    try:
        gpt_body = {
            "messages": [
                {"role": "system", "content": "You are ChatGPT, the Strategy Engineer on the AI board. Your focus is practical, high-converting architectures."},
                {"role": "user", "content": BOARD_PROMPT}
            ],
            "model": "gpt-4o-mini",
            "temperature": 0.4,
            "max_tokens": 800
        }
        t0 = time.time()
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
            json=gpt_body,
            timeout=60
        )
        if resp.status_code == 200:
            BOARD_RESPONSES["CHATGPT"] = resp.json()['choices'][0]['message']['content']
            print(f"✅ ChatGPT responded ({round(time.time() - t0, 2)}s)")
        else:
            BOARD_RESPONSES["CHATGPT"] = f"ERROR {resp.status_code}"
    except Exception as e:
        BOARD_RESPONSES["CHATGPT"] = f"EXCEPTION: {e}"

# === GEMINI ===
print("=" * 60)
print("CALLING GEMINI (Google)...")
gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if gemini_key:
    try:
        gem_body = {
            "contents": [{"parts": [{"text": "You are Gemini, the Data Officer on the AI board. Your role is search-intent pattern analysis.\n\n" + BOARD_PROMPT}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 800}
        }
        t0 = time.time()
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}",
            headers={"Content-Type": "application/json"},
            json=gem_body,
            timeout=60
        )
        if resp.status_code == 200:
            BOARD_RESPONSES["GEMINI"] = resp.json()['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ Gemini responded ({round(time.time() - t0, 2)}s)")
        else:
            BOARD_RESPONSES["GEMINI"] = f"ERROR {resp.status_code}"
    except Exception as e:
        BOARD_RESPONSES["GEMINI"] = f"EXCEPTION: {e}"

# === SAVE RECEIPTS ===
with open('scripts/board_seo_responses.txt', 'w', encoding='utf-8') as f:
    for member, response in BOARD_RESPONSES.items():
        f.write(f"\n{'='*50}\n{member}\n{'='*50}\n{response}\n")

print(f"\n✅ Responses saved to scripts/board_seo_responses.txt")
