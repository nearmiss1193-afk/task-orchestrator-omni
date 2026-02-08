
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
# BOARD INVESTIGATION: SMS Memory Works, Voice Memory Fails

## CURRENT STATUS (as of 2026-02-07 21:59 EST)
- ✅ **PRICING FIXED:** Sarah now says "$99/mo with 7 day trial" (confirmed working)
- ✅ **SMS MEMORY WORKS:** SMS channel remembers "Michael" correctly
- ❌ **VOICE MEMORY FAILS:** Phone calls don't remember caller name on callback

## THE MYSTERY
Same database. Same customer_memory table. But:
- SMS → Remembers name ✅
- Voice → Doesn't remember name ❌

## WHAT WE KNOW

### Database Schema (customer_memory table)
```sql
phone_number TEXT PRIMARY KEY
context_summary JSONB  -- Contains {"contact_name": "Dan", ...}
last_interaction TIMESTAMP
```

### SMS Handler (deploy.py ~line 216)
- Receives phone from GHL webhook
- Looks up customer_memory by phone_number
- WORKS - remembers "Michael"

### Voice Handler (deploy.py ~line 471)
- Receives phone from Vapi webhook
- Runs normalize_phone() on the number
- Looks up customer_memory by phone_number  
- FAILS - doesn't remember Dan

### Previous Fix Applied
Fixed code at line 507-508 to extract name from `context_summary.contact_name` instead of non-existent `customer_name` column.

## HYPOTHESES TO INVESTIGATE

### Hypothesis 1: Phone Number Format Mismatch
- SMS might store as "+13529368152"
- Voice might query as "13529368152" (no +)
- normalize_phone() might produce different format

### Hypothesis 2: Different Database Records
- SMS and Voice might be creating SEPARATE records
- One for "+1352..." 
- One for "1352..." (without +)

### Hypothesis 3: Vapi Event Timing
- Voice memory is saved on `end-of-call-report` event
- Memory lookup happens on `assistant-request` event
- Is the save completing before Vapi caches the assistant?

### Hypothesis 4: Vapi Assistant Caching
- Vapi might be caching the assistant config at session start
- Dynamic greeting injection might not be working
- Static assistant in dashboard overrides webhook response

### Hypothesis 5: SMS Uses Different Lookup Path
- SMS handler might use a different query pattern
- Perhaps SMS doesn't use normalize_phone() and matches raw number

## YOUR TASK

Board members, please analyze:

1. **Root Cause:** Which hypothesis is most likely? Or is there another cause?

2. **Evidence Needed:** What specific database queries or code inspection would prove/disprove each hypothesis?

3. **Why SMS Works:** Specifically explain WHY SMS memory retrieval succeeds while Voice fails, given they use the same table.

4. **Recommended Fix:** What code change would fix Voice memory WITHOUT breaking SMS?

5. **Verification Plan:** How can we verify the fix works before deployment?

Provide confidence level (high/medium/low) for your analysis.
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
