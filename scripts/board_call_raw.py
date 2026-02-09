
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
# BOARD STRATEGIC CORE AUDIT: Data Unification, Vapi Competence, & System Learning

## CONTEXT
The **'Empire Unified'** is scaling toward full autonomy. Dan is raising three critical structural concerns:
1. **Source of Truth (Lead Dashboard)**: We have data fragmented across Supabase, Resend (Email), GHL (CRM/SMS), and Vapi (Voice). We need a unified "Lead Truth" (Prospected -> Emailed -> SMSed -> Called).
2. **Vapi Competence Audit**: Sarah's memory failed even after a hard refresh. Are internal Vapi configuration settings (e.g., model selection, temperature, endpoint timeout, or 'Assistant Request' logic) sabotaging coherence?
3. **System Learning/Upgrade**: How well is the system "learning" from interactions and self-improving? (Reference: `self_healing_monitor` and `self_learning_cron`).

## THE QUESTIONS FOR THE BOARD
1. **The Unified Dashboard**: What is the most resilient architecture for a "Lead Source of Truth"? Should we use a Modal-driven Cron that periodically syncs Resend/GHL into a Master Supabase table, or a real-time event-driven bridge?
2. **Vapi Sabotage**: Beyond the 'Hard Refresh', what specific Vapi API settings or hidden dashboard configurations could be preventing "coherent" memory? (e.g., prompt length limits, specific model parameters).
3. **The Learning Audit**: How do we measure and upgrade the "System Intelligence"? What specific feedback loops are missing to make Sarah objectively smarter every day?
4. **ROI Check**: How do we reconcile Resend's delivery data with GHL's lead status to ensure we aren't "double-tapping" or wasting credits?

## YOUR TASK
Provide recommendations in three formats:
1. **Individual Perspectives**: Each AI's unique take.
2. **Collective Consensus**: Where you all agree.
3. **Steps to Success**: A numbered, actionable roadmap for Dan.

**STRICT CONSTRAINT: NO CODE OR FILE CHANGES.**
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
