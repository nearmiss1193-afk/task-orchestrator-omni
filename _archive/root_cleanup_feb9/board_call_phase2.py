import os, json, requests
from dotenv import load_dotenv
load_dotenv()

PROMPT = """# BOARD SESSION: System Optimization - Feb 9, 2026 3:22 PM EST

## CURRENT STATE (Verified Data)
- Outreach: 31 emails in last 30 min, 617 all-time
- SMS/Voice: ZERO in 24 hours despite 520 leads with phone numbers
- It is Monday 3 PM EST - SMS hours (8 AM - 6 PM Mon-Sat) are active
- Conversion: 1 interested lead from 617 touches (0.16%)
- 374 files in project root (massive clutter)
- 6 deprecated web_endpoint decorators in deploy.py
- Email is the ONLY channel that has ever fired

## THE 4 ISSUES

### Issue 1: SMS Not Firing (CRITICAL)
The outreach loop code:
1. Checks is_sms_hours (8-18 EST, Mon-Sat)
2. If phone exists AND is_sms_hours: calls dispatch_sms_logic.local(lead_id) then continue
3. Else if email exists: calls dispatch_email_logic.local(lead_id)

Yet all 617 touches are email. dispatch_sms_logic is a Modal @app.function. When called with .local() from within auto_outreach_loop (also Modal), it should work. But the except catches any error and just prints it, then continues (meaning it falls through to next lead, not email).

Possible root causes:
A) dispatch_sms_logic.local() is throwing an exception every time (e.g. Modal context issue)
B) The phone field values are empty string or null (not truly set)
C) is_sms_hours check is wrong (but code looks correct)

What is most likely and what is the fix?

### Issue 2: Email Conversion is 0.16% (1/617)
Only 1 lead reached interested status. Recommendations?

### Issue 3: Root Directory Cleanup (374 files)
Should we mass-archive? Risk vs reward?

### Issue 4: web_endpoint Deprecation
6 Modal endpoints use deprecated decorator. Fix now or wait?

## YOUR TASK
1. Recommendation on each issue
2. Priority order
3. Concise action plan
"""

results = {}

# Claude
try:
    import anthropic
    c = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    r = c.messages.create(model='claude-3-haiku-20240307', max_tokens=1000, messages=[{'role': 'user', 'content': PROMPT}])
    results['claude'] = r.content[0].text
    print('Claude: DONE')
except Exception as e:
    results['claude'] = f'ERROR: {e}'
    print(f'Claude: {e}')

# ChatGPT
try:
    from openai import OpenAI
    o = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    r = o.chat.completions.create(model='gpt-4o-mini', messages=[{'role': 'user', 'content': PROMPT}], max_tokens=1000)
    results['chatgpt'] = r.choices[0].message.content
    print('ChatGPT: DONE')
except Exception as e:
    results['chatgpt'] = f'ERROR: {e}'
    print(f'ChatGPT: {e}')

# Gemini
try:
    import google.generativeai as genai
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    m = genai.GenerativeModel('gemini-2.0-flash')
    r = m.generate_content(PROMPT)
    results['gemini'] = r.text
    print('Gemini: DONE')
except Exception as e:
    results['gemini'] = f'ERROR: {e}'
    print(f'Gemini: {e}')

# Grok
try:
    from openai import OpenAI
    g = OpenAI(api_key=os.environ.get('GROK_API_KEY'), base_url='https://api.x.ai/v1')
    r = g.chat.completions.create(model='grok-3-mini-fast', messages=[{'role': 'user', 'content': PROMPT}], max_tokens=1000)
    results['grok'] = r.choices[0].message.content
    print('Grok: DONE')
except Exception as e:
    results['grok'] = f'ERROR: {e}'
    print(f'Grok: {e}')

with open('board_call_phase2.json', 'w') as f:
    json.dump(results, f, indent=2)

ok = len([v for v in results.values() if not str(v).startswith('ERROR')])
print(f'\nBoard call complete. {ok}/4 responded.')
