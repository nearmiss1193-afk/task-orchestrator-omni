
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import google.generativeai as genai

# Load secrets
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

# 1. SETUP CLIENTS
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
xai = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
# 2. DEFINING THE BOARD PROMPT
PROMPT = """
# BOARD INVESTIGATION: Why Voice Memory Keeps Failing Despite "Fixes"

## CONTEXT - THE PATTERN
We have Sarah AI (Vapi voice assistant + SMS handler). Critical observation:
- ✅ SMS remembers name correctly (stored in Supabase customer_memory table)
- ❌ Voice STILL doesn't remember name on callback - **despite multiple "fixes"**

**THE PATTERN WE'RE INVESTIGATING:**
1. We identify a "root cause"
2. We apply a fix
3. We claim "success"
4. Dan reports it STILL doesn't work
5. Repeat cycle

This has happened 3+ times now. The board needs to analyze WHY this pattern keeps repeating.

## EVIDENCE GATHERED (Feb 8, 2026)

### What We Found:
1. **`vapi_debug_logs` table is EMPTY** - Zero entries
   - Our code has `log_to_debug_table()` that SHOULD log to this table on every call
   - If no logs exist, either: (a) webhook isn't being called, or (b) logging fails silently

2. **`conversation_logs` has a column mismatch error** (Postgres error 42703)
   - The INSERT statement may be referencing columns that don't exist

3. **Code looks correct** - The vapi_webhook function in deploy.py:
   - Uses normalize_phone() for consistency ✅
   - Looks up customer_memory correctly ✅
   - Builds personalized greeting with customer_name ✅
   - Has extensive print statements for debugging ✅

4. **SMS uses the same database and phone normalization and IT WORKS**

### The Question:
If the code is correct, why isn't it working? Where is the silent failure?

## QUESTIONS FOR THE BOARD

### 1. What Are The Most Likely Silent Failure Points?
Given the evidence (empty debug logs, correct-looking code, SMS works but Voice doesn't):
- Is Vapi even calling our serverUrl webhook?
- Is there a Vapi assistant configuration issue (wrong serverUrl setting)?
- Does Vapi cache assistant configs and ignore webhook updates?
- Is our Modal endpoint actually deployed with the latest code?

### 2. Why Do Our "Fixes" Keep Not Working?
We keep applying code fixes that look correct but don't solve the problem. Why?
- Are we fixing symptoms instead of root causes?
- Is there a configuration layer we're not checking?
- Is there a verification step we're skipping?

### 3. What Is The Proper Diagnostic Sequence?
What should we check IN ORDER to find the ACTUAL failure point?
Propose a step-by-step diagnostic protocol.

### 4. Who Has Successfully Built Vapi + External Memory?
- Is there a reference implementation we can study?
- What gotchas have others encountered?
- Is serverUrl webhook the right approach, or is there a better pattern?

## YOUR TASK

Each board member should provide:
1. **Your hypothesis** - What do YOU think is failing?
2. **Evidence that would confirm your hypothesis** - What specific test would prove it?
3. **Recommended next step** - What should we check FIRST?
4. **Confidence level** (high/medium/low)

BE SPECIFIC. Don't give generic advice. Give actionable diagnostic steps.

## CONSTRAINTS
- Discovery only. NO CODE CHANGES until we find the real root cause.
- We use: Vapi, Supabase, Modal, GHL
- Dan is frustrated with the "fixed it, oops still doesn't work" cycle
"""








def call_board():
    responses = {}
    
    # CLAUDE
    try:
        msg = claude.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": PROMPT}]
        )
        responses["Claude"] = msg.content[0].text
    except Exception as e:
        responses["Claude"] = str(e)

    # CHATGPT
    try:
        completion = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": PROMPT}]
        )
        responses["ChatGPT"] = completion.choices[0].message.content
    except Exception as e:
        responses["ChatGPT"] = str(e)

    # GEMINI
    try:
        # 'gemini-1.5-flash' is the stable latest model
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        response = model.generate_content(PROMPT)
        responses["Gemini"] = response.text
    except Exception as e:
        responses["Gemini"] = f"Gemini Error: {str(e)}"

    # GROK (xAI)
    try:
        # CORRECTED VARIABLE NAME (Found via diagnostics)
        api_key = os.getenv("GROK_API_KEY") 
        
        if not api_key:
             responses["Grok"] = "SKIPPED: GROK_API_KEY missing in .secrets.env"
        else:
            client = OpenAI(
                api_key=api_key, 
                base_url="https://api.x.ai/v1"
            )
            completion = client.chat.completions.create(
                model="grok-3",
                messages=[{"role": "system", "content": "You are a strategic board member."},
                        {"role": "user", "content": PROMPT}]
            )
            responses["Grok"] = completion.choices[0].message.content
    except Exception as e:
        responses["Grok"] = f"Grok Error: {str(e)}"

    # SAVE RESULTS
    with open("board_call_raw.json", "w") as f:
        json.dump(responses, f, indent=2)
    
    print("✅ Board meeting adjourned. Results saved to board_call_raw.json")

if __name__ == "__main__":
    call_board()
