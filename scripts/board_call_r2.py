"""
BOARD CALL ROUND 2 - Post-fix findings
"""
import requests, os, json, time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

RECEIPTS = []
BOARD_RESPONSES = {}

def log_receipt(member, endpoint, status, req_preview, resp_preview):
    RECEIPTS.append({"timestamp": datetime.now().isoformat(), "board_member": member, 
                     "endpoint": endpoint, "http_status": status, 
                     "request_preview": req_preview[:200], "response_preview": resp_preview[:500]})

diag = open('scripts/post_fix_diagnosis.txt', 'r', encoding='utf-8').read()

PROMPT = f"""You are on the AI Board. We applied 6 fixes. Some things improved but Dan says it's still not working. Analyze what SPECIFICALLY is still broken from this UPDATED diagnostic data:

{diag}

KEY CONTEXT:
- We fixed both assistant serverUrls - they now point to our webhook (VERIFIED in section 4)
- BUT 3 phone numbers (8636928474, 8633373601, 8633373705) still point to OLD dead endpoint "empire-inbound-vapi-webhook"
- Voice call at 20:40 DID get logged to conversation_logs (section 2) - webhook IS firing
- SMS at 20:05 still said "Michael" but that was BEFORE our deploy at 20:14 UTC
- SMS at 20:03-20:04 correctly said "Daniel" AFTER the name correction was told to Sarah

QUESTIONS FOR THE BOARD:
1. What is STILL broken right now?
2. Are the phone number serverUrls the remaining issue for call notifications?
3. Why might Dan still experience problems even though voice logging works?
4. What should we fix next? Be SPECIFIC.

Keep under 250 words."""

grok_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
openai_key = os.environ.get("OPENAI_API_KEY")
gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

# GROK
print("Calling Grok...")
try:
    body = {"messages": [{"role": "system", "content": "You are Grok, Intelligence Officer. Be precise and data-driven."}, {"role": "user", "content": PROMPT}], "model": "grok-3-mini", "temperature": 0.3, "max_tokens": 500}
    r = requests.post("https://api.x.ai/v1/chat/completions", headers={"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"}, json=body, timeout=60)
    reply = r.json()['choices'][0]['message']['content'] if r.status_code == 200 else f"ERROR {r.status_code}"
    BOARD_RESPONSES["GROK"] = reply
    log_receipt("GROK", "api.x.ai", r.status_code, json.dumps(body)[:200], r.text[:500])
    print(f"  ✅ {r.status_code}")
except Exception as e:
    BOARD_RESPONSES["GROK"] = f"EXCEPTION: {e}"

# CHATGPT
print("Calling ChatGPT...")
try:
    body = {"messages": [{"role": "system", "content": "You are ChatGPT, the Engineer. Focus on code-level fixes."}, {"role": "user", "content": PROMPT}], "model": "gpt-4o-mini", "temperature": 0.3, "max_tokens": 500}
    r = requests.post("https://api.openai.com/v1/chat/completions", headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}, json=body, timeout=60)
    reply = r.json()['choices'][0]['message']['content'] if r.status_code == 200 else f"ERROR {r.status_code}"
    BOARD_RESPONSES["CHATGPT"] = reply
    log_receipt("CHATGPT", "api.openai.com", r.status_code, json.dumps(body)[:200], r.text[:500])
    print(f"  ✅ {r.status_code}")
except Exception as e:
    BOARD_RESPONSES["CHATGPT"] = f"EXCEPTION: {e}"

# GEMINI
print("Calling Gemini...")
try:
    body = {"contents": [{"parts": [{"text": "You are Gemini, Data Officer. Focus on patterns.\n\n" + PROMPT}]}], "generationConfig": {"temperature": 0.3, "maxOutputTokens": 500}}
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}", headers={"Content-Type": "application/json"}, json=body, timeout=60)
    reply = r.json()['candidates'][0]['content']['parts'][0]['text'] if r.status_code == 200 else f"ERROR {r.status_code}"
    BOARD_RESPONSES["GEMINI"] = reply
    log_receipt("GEMINI", "googleapis.com", r.status_code, json.dumps(body)[:200], r.text[:500])
    print(f"  ✅ {r.status_code}")
except Exception as e:
    BOARD_RESPONSES["GEMINI"] = f"EXCEPTION: {e}"

# ANTIGRAVITY
BOARD_RESPONSES["ANTIGRAVITY"] = """From direct data analysis:
1. STILL BROKEN: 3 phone numbers (8636928474, 8633373601, 8633373705) have phone-level serverUrl pointing to DEAD 'empire-inbound' endpoint. Phone-level URL can override assistant-level per Vapi docs.
2. WORKING: Voice webhook IS firing (call at 20:40 logged). SMS name fix works for messages after deploy.
3. DAN EXPERIENCE: If Dan called from a number routed through one of those 3 phones, the phone-level serverUrl sent the webhook to the dead endpoint.
4. FIX: Update serverUrl on all 3 phone numbers to our current webhook URL."""

# Save
with open('scripts/board2_responses.txt', 'w', encoding='utf-8') as f:
    for m, r in BOARD_RESPONSES.items():
        f.write(f"\n{'='*50}\n{m}\n{'='*50}\n{r}\n")

with open('scripts/board2_receipts.txt', 'w', encoding='utf-8') as f:
    f.write(f"BOARD CALL 2 RECEIPTS - {datetime.now().isoformat()}\n")
    for r in RECEIPTS:
        f.write(f"\n--- {r['board_member']} ---\nTimestamp: {r['timestamp']}\nEndpoint: {r['endpoint']}\nHTTP: {r['http_status']}\nRequest: {r['request_preview']}\nResponse: {r['response_preview']}\n")

print(f"\n✅ Board call 2 complete. {len(RECEIPTS)} API calls logged.")
