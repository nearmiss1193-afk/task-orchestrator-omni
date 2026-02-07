
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

**INVESTIGATION TOPIC: Sarah Inbound vs Outbound Call Detection**

## CURRENT STATE
Sarah is our AI voice assistant powered by Vapi.ai. She has:
- Different prompt scripts for INBOUND calls ("Hey thanks for calling! This is Sarah...")  
- Different prompt scripts for OUTBOUND calls ("Hey, is this [name]?")

## KEY QUESTIONS

### Q1: Can Vapi detect call direction automatically?
- Does Vapi provide metadata indicating if a call is inbound vs outbound?
- What webhook fields contain this information?
- Is this available BEFORE the call starts or only after?

### Q2: How should Sarah dynamically switch behavior?
- Should we use serverUrl webhooks to inject call type into the prompt?
- Should we create 2 separate assistants (one for inbound, one for outbound)?
- Should we use Vapi's assistant overrides feature?

### Q3: What about knowing WHERE the lead came from?
- If someone calls in, can we know if they saw an ad, got an SMS, visited website?
- Can we pass UTM parameters or source tags to voice calls?
- How do we link an inbound caller to their existing lead record?

### Q4: Cross-channel continuity
- If we SMS a lead, then they call back, how does Sarah know this is the same person?
- Phone number matching? GHL contact ID lookup?
- How do we sync context between SMS Sarah and Voice Sarah?

## CONTEXT
- Voice Platform: Vapi.ai (using Groq LLM)
- Backend: Modal (Python serverless)
- Database: Supabase (customer_memory table with phone number key)
- CRM: GoHighLevel
- Current serverUrl: https://nearmiss1193-afk--vapi-live.modal.run

## WHAT WE NEED
1. Technical answer: Can Vapi detect inbound vs outbound?
2. Best practice: Single assistant or multiple?
3. Implementation: How to pass call type to the assistant
4. Source tracking: Can we know where the caller came from?
5. Memory sync: Best way to link voice calls to existing customer_memory records

**FORMAT:**
- Q1 Answer: [Your findings]
- Q2 Answer: [Your recommendation]
- Q3 Answer: [Your findings]
- Q4 Answer: [Your recommendation]
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
