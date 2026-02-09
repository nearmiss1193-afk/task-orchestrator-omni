
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import google.generativeai as genai

# Load secrets
load_dotenv(r"C:\Users\nearm\.gemini\antigravity\scratch\empire-unified\.secrets\secrets.env")

PROMPT = """
# BOARD EMERGENCY SESSION: System Recovery & Architecture Consolidation

## CONTEXT
The 'Empire Unified' outreach system has been STALLED for 10 days (Jan 30 - Feb 9, 2026).

**Root Cause Found:** All 615 leads were moved to non-contactable statuses (outreach_sent, contacted, failed). The auto_outreach_loop CRON runs every 5 min but queries only status IN ('new', 'research_done') - found 0 leads, did nothing for 10 days.

**Fix Applied:** Reset lead statuses to 'new'. But deeper architectural issues remain.

## THE 4 CRITICAL ISSUES REQUIRING BOARD OPINION

### ISSUE 1: TWO DEPLOY FILES (LANDMINE)
Both `deploy.py` (918 lines) and `master_deploy.py` (162 lines) define the SAME Modal app name `ghl-omni-automation`. 
- `deploy.py` imports from `workers/outreach.py` - has real GHL webhook calls for email/SMS
- `master_deploy.py` has INLINE logic that only inserts rows into `outbound_touches` but does NOT actually send emails via GHL webhook

**Whichever was deployed last overwrites the other.** We don't know which is live.

**Question:** Should we consolidate to ONE file? Which logic should survive - the `deploy.py` version with real webhook calls, or do we rebuild from `master_deploy.py` (simpler but doesn't actually send)?

### ISSUE 2: LEAD RECYCLING (PREVENTS FUTURE STALLS)
Once all leads get status 'outreach_sent', the queue empties and outreach silently stops. No error, no alert.

**Question:** What's the best recycling strategy?
- Option A: Daily CRON resets leads to 'new' after 7 days of no response
- Option B: Add more statuses to the contactable query (e.g., include 'outreach_sent' leads after cooldown)
- Option C: Separate "follow-up" queue with escalating channels (email -> SMS -> call)

**Constraint:** Modal Starter Plan = 5 CRON limit. We currently use 4.

### ISSUE 3: DEAD MODAL APPS
4 stale apps wasting resources:
- `empire-api-v3` - CRASH-LOOPING (2000 inputs, 0 containers)
- `test-atomic` - 0 calls in 13 days
- `nexus-portal` - 0 calls in 11 days
- `nexus-engine` - dispatch_call has 135/135 errors (100% failure rate)

**Question:** Safe to stop all 4? Any dependencies we might miss?

### ISSUE 4: VERIFYING ACTUAL EMAIL DELIVERY
The outreach loop logs rows in `outbound_touches` but does the email actually reach the prospect's inbox? The `master_deploy.py` version just logs "truth_verification" payloads without calling GHL webhook.

**Question:** What's the minimum viable verification we need? Should we:
- Option A: Check GHL for sent email confirmation
- Option B: Add Resend delivery webhooks
- Option C: Manual spot-check of 5 emails
- Option D: Add email open tracking pixel

## YOUR TASK
1. Give your recommendation on each issue (1-4)
2. Flag any risks or dependencies I might be missing
3. Provide a prioritized action plan (what to fix first)

**FORMAT: Be concise. Numbered recommendations. No code changes - strategy only.**
"""

def call_board():
    responses = {}
    
    # CLAUDE
    try:
        msg = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")).messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1500,
            messages=[{"role": "user", "content": PROMPT}]
        )
        responses["Claude"] = msg.content[0].text
        print("Claude: RESPONDED")
    except Exception as e:
        responses["Claude"] = f"Error: {str(e)}"
        print(f"Claude: FAILED - {e}")

    # CHATGPT
    try:
        completion = OpenAI(api_key=os.getenv("OPENAI_API_KEY")).chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": PROMPT}]
        )
        responses["ChatGPT"] = completion.choices[0].message.content
        print("ChatGPT: RESPONDED")
    except Exception as e:
        responses["ChatGPT"] = f"Error: {str(e)}"
        print(f"ChatGPT: FAILED - {e}")

    # GEMINI
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        response = model.generate_content(PROMPT)
        responses["Gemini"] = response.text
        print("Gemini: RESPONDED")
    except Exception as e:
        responses["Gemini"] = f"Error: {str(e)}"
        print(f"Gemini: FAILED - {e}")

    # GROK (xAI)
    try:
        api_key = os.getenv("GROK_API_KEY")
        if not api_key:
            responses["Grok"] = "SKIPPED: GROK_API_KEY missing"
            print("Grok: SKIPPED")
        else:
            client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
            completion = client.chat.completions.create(
                model="grok-3",
                messages=[{"role": "system", "content": "You are a strategic board member advising on system architecture."},
                         {"role": "user", "content": PROMPT}]
            )
            responses["Grok"] = completion.choices[0].message.content
            print("Grok: RESPONDED")
    except Exception as e:
        responses["Grok"] = f"Error: {str(e)}"
        print(f"Grok: FAILED - {e}")

    # SAVE RESULTS
    with open("board_session_feb9.json", "w") as f:
        json.dump(responses, f, indent=2)
    
    # Print summary
    print("\n" + "="*70)
    print("BOARD SESSION COMPLETE")
    print("="*70)
    responded = [k for k, v in responses.items() if not v.startswith("Error") and not v.startswith("SKIPPED")]
    failed = [k for k, v in responses.items() if v.startswith("Error") or v.startswith("SKIPPED")]
    print(f"Responded: {len(responded)}/4 - {', '.join(responded)}")
    if failed:
        print(f"Failed: {', '.join(failed)}")
    print(f"\nFull results saved to board_session_feb9.json")

if __name__ == "__main__":
    call_board()
