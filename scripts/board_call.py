"""
REAL BOARD CALL - Makes actual API calls to AI board members
Every request/response is logged to board_receipts.txt as PROOF
"""
import requests, os, json, time
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
load_dotenv('.env.local')

RECEIPTS = []
BOARD_RESPONSES = {}

def log_receipt(board_member, endpoint, status_code, request_body_preview, response_preview):
    """Log every API call as a verifiable receipt"""
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

# The diagnostic data each board member will analyze
DIAGNOSTIC_BRIEFING = open('scripts/full_diagnosis.txt', 'r', encoding='utf-8').read()

BOARD_PROMPT = f"""You are on the AI Board of Directors for an automation company. You are reviewing a diagnostic report about system failures.

DIAGNOSTIC DATA:
{DIAGNOSTIC_BRIEFING}

SYMPTOMS REPORTED BY THE CEO (Dan):
1. Call notifications do NOT work - no notification when someone calls Sarah AI
2. SMS notifications DO work now (just got fixed)
3. Sarah still calls the customer "Michael" even after being told his name is Daniel
4. SMS conversation loops - Sarah asks the same authority question every message
5. No memory between calls - Sarah forgets everything between voice calls
6. After replying to Sarah's first SMS, the second reply got no response

Give your analysis in this format:
1. ROOT CAUSE (what is the #1 thing causing the most problems)
2. QUICK WINS (what can be fixed in under 30 minutes)  
3. RISKS (what will break if we don't fix it soon)
4. RECOMMENDED FIX ORDER (numbered priority list)

Keep it under 300 words. Be specific - reference the actual data."""

# === BOARD MEMBER: GROK (xAI) ===
print("=" * 60)
print("CALLING GROK (xAI)...")
print("=" * 60)
grok_key = os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY")
if grok_key:
    try:
        grok_body = {
            "messages": [
                {"role": "system", "content": "You are Grok, the Intelligence Officer on the AI board. Your role is deep technical analysis."},
                {"role": "user", "content": BOARD_PROMPT}
            ],
            "model": "grok-3-mini",
            "temperature": 0.3,
            "max_tokens": 600
        }
        t0 = time.time()
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {grok_key}", "Content-Type": "application/json"},
            json=grok_body,
            timeout=60
        )
        elapsed = round(time.time() - t0, 2)
        
        if resp.status_code == 200:
            grok_reply = resp.json()['choices'][0]['message']['content']
            BOARD_RESPONSES["GROK"] = grok_reply
            print(f"✅ Grok responded ({elapsed}s)")
            print(grok_reply)
        else:
            BOARD_RESPONSES["GROK"] = f"ERROR {resp.status_code}: {resp.text[:200]}"
            print(f"❌ Grok error: {resp.status_code}")
        
        log_receipt("GROK", "https://api.x.ai/v1/chat/completions", resp.status_code, 
                   json.dumps(grok_body)[:200], resp.text[:500])
    except Exception as e:
        BOARD_RESPONSES["GROK"] = f"EXCEPTION: {e}"
        log_receipt("GROK", "https://api.x.ai/v1/chat/completions", 0, "", str(e))
        print(f"❌ Grok exception: {e}")
else:
    BOARD_RESPONSES["GROK"] = "NO API KEY AVAILABLE"
    log_receipt("GROK", "N/A", 0, "NO KEY", "GROK_API_KEY not found in env")
    print("❌ No Grok API key found")

# === BOARD MEMBER: OPENAI (ChatGPT) ===
print("\n" + "=" * 60)
print("CALLING CHATGPT (OpenAI)...")
print("=" * 60)
openai_key = os.environ.get("OPENAI_API_KEY")
if openai_key:
    try:
        gpt_body = {
            "messages": [
                {"role": "system", "content": "You are ChatGPT, the Engineer on the AI board. Your role is practical code-level fixes."},
                {"role": "user", "content": BOARD_PROMPT}
            ],
            "model": "gpt-4o-mini",
            "temperature": 0.3,
            "max_tokens": 600
        }
        t0 = time.time()
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
            json=gpt_body,
            timeout=60
        )
        elapsed = round(time.time() - t0, 2)
        
        if resp.status_code == 200:
            gpt_reply = resp.json()['choices'][0]['message']['content']
            BOARD_RESPONSES["CHATGPT"] = gpt_reply
            print(f"✅ ChatGPT responded ({elapsed}s)")
            print(gpt_reply)
        else:
            BOARD_RESPONSES["CHATGPT"] = f"ERROR {resp.status_code}: {resp.text[:200]}"
            print(f"❌ ChatGPT error: {resp.status_code}")
        
        log_receipt("CHATGPT", "https://api.openai.com/v1/chat/completions", resp.status_code,
                   json.dumps(gpt_body)[:200], resp.text[:500])
    except Exception as e:
        BOARD_RESPONSES["CHATGPT"] = f"EXCEPTION: {e}"
        log_receipt("CHATGPT", "https://api.openai.com/v1/chat/completions", 0, "", str(e))
        print(f"❌ ChatGPT exception: {e}")
else:
    BOARD_RESPONSES["CHATGPT"] = "NO API KEY AVAILABLE"
    log_receipt("CHATGPT", "N/A", 0, "NO KEY", "OPENAI_API_KEY not found in env")
    print("❌ No OpenAI API key found")

# === BOARD MEMBER: GEMINI (Google) ===
print("\n" + "=" * 60)
print("CALLING GEMINI (Google)...")
print("=" * 60)
gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if gemini_key:
    try:
        gem_body = {
            "contents": [{"parts": [{"text": "You are Gemini, the Data Officer on the AI board. Your role is pattern analysis.\n\n" + BOARD_PROMPT}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 600}
        }
        t0 = time.time()
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}",
            headers={"Content-Type": "application/json"},
            json=gem_body,
            timeout=60
        )
        elapsed = round(time.time() - t0, 2)
        
        if resp.status_code == 200:
            gem_reply = resp.json()['candidates'][0]['content']['parts'][0]['text']
            BOARD_RESPONSES["GEMINI"] = gem_reply
            print(f"✅ Gemini responded ({elapsed}s)")
            print(gem_reply)
        else:
            BOARD_RESPONSES["GEMINI"] = f"ERROR {resp.status_code}: {resp.text[:200]}"
            print(f"❌ Gemini error: {resp.status_code}")
        
        log_receipt("GEMINI", "generativelanguage.googleapis.com", resp.status_code,
                   json.dumps(gem_body)[:200], resp.text[:500])
    except Exception as e:
        BOARD_RESPONSES["GEMINI"] = f"EXCEPTION: {e}"
        log_receipt("GEMINI", "generativelanguage.googleapis.com", 0, "", str(e))
        print(f"❌ Gemini exception: {e}")
else:
    BOARD_RESPONSES["GEMINI"] = "NO API KEY AVAILABLE"
    log_receipt("GEMINI", "N/A", 0, "NO KEY", "GEMINI_API_KEY not found in env")
    print("❌ No Gemini API key found")

# === ANTIGRAVITY SYNTHESIS (me - using the diagnostic data directly) ===
print("\n" + "=" * 60)
print("ANTIGRAVITY SYNTHESIS (from direct data)")
print("=" * 60)
BOARD_RESPONSES["ANTIGRAVITY"] = """Based on direct Supabase + Vapi API queries:
1. ROOT CAUSE: Calls route to assistant 1a797f12 (NOT Sarah ae717f29). Our serverUrl fix was applied to the wrong assistant.
2. QUICK WINS: (a) Fix Michael name in customer_memory, (b) Create vapi_call_notifications table
3. RISKS: Real customers will get called Michael and Sarah will loop on them
4. FIX ORDER: (1) Identify which phone Dan calls and fix that assistant's serverUrl, (2) Clear Michael from context_summary, (3) Fix name extraction logic, (4) Fix conversation flow"""
print(BOARD_RESPONSES["ANTIGRAVITY"])

# === SAVE RECEIPTS ===
print("\n" + "=" * 60)
print("SAVING RECEIPTS (proof of real API calls)")
print("=" * 60)

receipt_output = []
receipt_output.append("=" * 60)
receipt_output.append("BOARD CALL RECEIPTS - PROOF OF REAL API CALLS")
receipt_output.append(f"Generated: {datetime.now().isoformat()}")
receipt_output.append("=" * 60)

for r in RECEIPTS:
    receipt_output.append(f"\n--- {r['board_member']} ---")
    receipt_output.append(f"Timestamp: {r['timestamp']}")
    receipt_output.append(f"Endpoint: {r['endpoint']}")
    receipt_output.append(f"HTTP Status: {r['http_status']}")
    receipt_output.append(f"Request: {r['request_preview']}")
    receipt_output.append(f"Response: {r['response_preview']}")

receipt_output.append("\n" + "=" * 60)
receipt_output.append("FULL BOARD RESPONSES")
receipt_output.append("=" * 60)

for member, response in BOARD_RESPONSES.items():
    receipt_output.append(f"\n{'='*40}")
    receipt_output.append(f"{member}")
    receipt_output.append(f"{'='*40}")
    receipt_output.append(response)

with open('scripts/board_receipts.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(receipt_output))

with open('scripts/board_responses.txt', 'w', encoding='utf-8') as f:
    for member, response in BOARD_RESPONSES.items():
        f.write(f"\n{'='*50}\n{member}\n{'='*50}\n{response}\n")

print(f"\n✅ Receipts saved to scripts/board_receipts.txt")
print(f"✅ Responses saved to scripts/board_responses.txt")
print(f"✅ {len(RECEIPTS)} API calls logged with proof")
