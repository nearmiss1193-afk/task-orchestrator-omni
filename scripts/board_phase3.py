"""
BOARD CALL - Phase 3: Revenue Optimization
3 Priorities: Email/SMS Tracking, Email Conversion, SCRAPED_ Lead Enrichment
"""
import os, json, requests, time
from dotenv import load_dotenv
load_dotenv()

BOARD_BRIEF = """
BOARD BRIEF - Phase 3: Revenue Optimization (Feb 9, 2026 3:55 PM EST)

CURRENT DATA:
- 615 total leads in contacts_master
- 427 fresh leads (new/research_done status)
- 444 leads have fake SCRAPED_ GHL IDs (can't receive SMS via GHL webhook)
- 171 leads have real GHL IDs
- Email conversion: 0.16% (abysmal)
- ai_strategy field: 411/615 are NULL (67% get generic fallback email body)
- Current email subject: "quick question" (same for all)
- Current email body fallback: "hey, saw your site and had a question"
- SMS just fixed (was 0, now 178 sent to real GHL leads)

CURRENT EMAIL DISPATCH:
- Uses GHL webhook with payload: contact_id, first_name, email, subject ("quick question"), body (ai_strategy or fallback)
- No open tracking, no click tracking, no delivery status tracking
- No follow-up sequence (one-shot only)
- Same subject line for ALL leads

SYSTEM: Modal (Python) → GHL webhooks for delivery. Supabase for data.

3 QUESTIONS FOR THE BOARD:

1. EMAIL/SMS TRACKING INFRASTRUCTURE:
   Owner wants 100% tracking on ALL outreach forever: opens, clicks, delivery status, bounces.
   Options:
   A. Use GHL's built-in tracking (opens/clicks already tracked in GHL if emails go through GHL campaigns/workflows)
   B. Switch from webhook to GHL API direct send (gives us event webhooks back for tracking)
   C. Add our own tracking layer (pixel tracking, link wrapping) before sending via webhook
   D. Use Resend API (already in stack) which has built-in open/click/bounce webhooks
   
   Which approach gives us the best tracking with least complexity? How do we store and report on this data?

2. EMAIL CONVERSION FIX (0.16% → 5%+):
   67% of leads get a generic "hey, saw your site and had a question" email.
   Current subject: "quick question" for everyone.
   How do we fix this? Consider:
   - Better personalization with available data (company_name, website_url, niche)
   - A/B testing subject lines
   - Follow-up sequences (day 1, day 3, day 7)
   - bfisher-style cold email format vs current generic style
   
3. SCRAPED_ LEADS → REAL GHL CONTACTS:
   444 leads have GHL IDs like "SCRAPED_e1dbae35" — these are NOT real GHL contacts.
   These can't receive SMS or properly tracked emails via GHL.
   Options:
   A. Use GHL Contacts API to CREATE real contacts for each SCRAPED_ lead (bulk)
   B. Use GHL's import CSV feature manually
   C. Build an automated sync: when lead is scraped, immediately create GHL contact
   D. Skip GHL for these, send directly via Resend (email) and Twilio (SMS)
   
   Which approach? The GHL API endpoint is POST /contacts with location_id.

Please respond with specific, actionable recommendations for all 3 questions.
"""

results = {}

# ChatGPT
try:
    r = requests.post("https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', '')}"},
        json={"model": "gpt-4o-mini", "messages": [
            {"role": "system", "content": "You are a digital marketing and CRM automation expert on the board of a lead gen agency. Give specific, actionable advice. Be concise."},
            {"role": "user", "content": BOARD_BRIEF}
        ], "max_tokens": 1000, "temperature": 0.7}, timeout=30)
    results['chatgpt'] = r.json()['choices'][0]['message']['content']
    print("ChatGPT: OK")
except Exception as e:
    results['chatgpt'] = f"ERROR: {e}"
    print(f"ChatGPT: {e}")

# Gemini
try:
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.environ.get('GOOGLE_API_KEY', '')}",
        json={"contents": [{"parts": [{"text": "You are a digital marketing and CRM expert on the board of a lead gen agency. " + BOARD_BRIEF}]}],
              "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.7}}, timeout=30)
    data = r.json()
    results['gemini'] = data['candidates'][0]['content']['parts'][0]['text']
    print("Gemini: OK")
except Exception as e:
    results['gemini'] = f"ERROR: {e}"
    print(f"Gemini: {e}")

# Grok
try:
    r = requests.post("https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ.get('XAI_API_KEY', '')}"},
        json={"model": "grok-3-mini-fast", "messages": [
            {"role": "system", "content": "You are a digital marketing and CRM expert on the board of a lead gen agency. Give specific, actionable advice."},
            {"role": "user", "content": BOARD_BRIEF}
        ], "max_tokens": 1000, "temperature": 0.7}, timeout=30)
    results['grok'] = r.json()['choices'][0]['message']['content']
    print("Grok: OK")
except Exception as e:
    results['grok'] = f"ERROR: {e}"
    print(f"Grok: {e}")

# Claude
try:
    r = requests.post("https://api.anthropic.com/v1/messages",
        headers={"x-api-key": os.environ.get('ANTHROPIC_API_KEY', ''),
                 "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": "claude-sonnet-4-20250514", "max_tokens": 1000,
              "messages": [{"role": "user", "content": "You are a digital marketing and CRM expert. " + BOARD_BRIEF}]}, timeout=30)
    data = r.json()
    results['claude'] = data['content'][0]['text']
    print("Claude: OK")
except Exception as e:
    results['claude'] = f"ERROR: {e}"
    print(f"Claude: {e}")

# Save results
with open("scripts/board_phase3_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n=== BOARD RESPONSES ===")
for name, resp in results.items():
    print(f"\n--- {name.upper()} ---")
    print(resp[:2000])
    print()
