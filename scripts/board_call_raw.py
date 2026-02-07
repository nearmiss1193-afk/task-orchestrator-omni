
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
You are a strategic advisor for AI Service Co, a B2B service agency selling AI automation to local businesses.

**RESEARCH TOPICS (Fact-Finding Only):**

## TOPIC 1: UNIVERSAL SARAH LOGIC
How should we implement UNIFIED behavior for Sarah (AI assistant) across ALL channels?
- SMS inbound/outbound
- Voice calls (Vapi) inbound/outbound
- Website chat (if applicable)

Current Problem: Sarah has different prompts/logic per channel, which could cause conflicting information.

## TOPIC 2: PERSISTENT CUSTOMER MEMORY
How should Sarah maintain memory of customer conversations across:
- Multiple SMS exchanges
- Inbound calls → Outbound calls (same customer)
- Outbound calls → Customer calls back
- Cross-channel (SMS then call, or call then SMS)

Requirements:
1. Sarah should recognize returning customers
2. Sarah should NOT repeat questions already answered
3. Sarah should remember context from previous conversations
4. Memory should persist until customer converts or is marked dead

## TOPIC 3: SELF-HEALING & AUTONOMOUS OPERATION
How do we make Sarah's system run 24/7 without manual intervention?
- Auto-detect crashes or API failures
- Auto-restart failed services
- Alert owner only when human intervention truly needed
- Log all issues for later review

Current Problem: System requires manual monitoring and restarts after crashes.

**WHAT WE NEED:**
1. Architecture recommendations for unified logic
2. Database schema for customer memory
3. Technical approach for cross-channel memory sync
4. Self-healing implementation patterns
5. Monitoring & alerting strategy

**CONTEXT:**
- Backend: Modal (Python serverless)
- Database: Supabase (PostgreSQL)
- Voice: Vapi.ai
- SMS/Email: GHL webhooks
- CRM: GoHighLevel

**YOUR TASK:**
Provide technical recommendations for each topic. Be specific about:
- Database tables needed
- How to store/retrieve conversation context
- How to sync across channels
- How to implement self-healing
- What monitoring is needed

**FORMAT:**
- Topic 1: [Your recommendations]
- Topic 2: [Your recommendations]  
- Topic 3: [Your recommendations]
- Key Warnings: [Any concerns or gotchas]
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
