## 🚨 CRITICAL: READ FIRST BEFORE ANY ACTION (Updated Feb 5, 2026)

### INFRASTRUCTURE (NEVER ASK USER)

| Key | Value | Notes |
|-----|-------|-------|
| **HOSTING_PROVIDER** | **Vercel** | User confirmed: "I have been on Vercel forever" |
| **DOMAIN_REGISTRAR** | **Squarespace** | DNS managed by Squarespace, points to Vercel |
| **PRODUCTION_DOMAIN** | **aiserviceco.com** | THE ONLY DOMAIN TO VERIFY - NOT netlify subdomain |
| **DEPLOY_COMMAND** | `vercel --prod --yes` | Run from public/ directory |
| **STAGING_DOMAIN** | aiserviceco-empire.netlify.app | STAGING ONLY - never verify as production |

### HARD RULES (MANDATORY)

1. **ALWAYS deploy to Vercel** - `cd public && vercel --prod --yes`
2. **ALWAYS verify aiserviceco.com** - NOT netlify subdomain
3. **NEVER ask user about hosting** - Info is RIGHT HERE
4. **BEFORE claiming success**: Open browser to aiserviceco.com and verify

### NON-LOCAL PROSPECTING (MANDATORY - Added Feb 5, 2026)

> [!CAUTION]
> **PROSPECTING MUST BE NON-LOCAL**
> PageSpeed audits, web scraping, and prospect research MUST run on Modal cloud - NOT locally.

| What | How | Why |
|------|-----|-----|
| **PageSpeed Audits** | Modal function or PageSpeed API | Avoid rate limits, consistent results |
| **Web Scraping** | Modal with Playwright | Distributed, avoid IP blocks |
| **Email Verification** | Modal or API | Server-side validation |
| **Lead Research** | Modal cron jobs | 24/7 automated prospecting |

**Implementation:**

- Use `deploy.py` to add Modal endpoints for prospecting
- Store results in Supabase for persistence
- Pre-run audits, don't run at email-send time

### GHL API LIMITATION (CRITICAL - VERIFIED Feb 5, 2026)

> [!CAUTION]
> **GHL API DOES NOT WORK** - Private integration only!
> **MUST USE WEBHOOKS** for all GHL email/SMS

| What | Status | Solution |
|------|--------|----------|
| GHL REST API | ❌ DOES NOT WORK | Private integration - not accessible |
| GHL Webhooks | ✅ WORKS | Use webhook URLs from reliable_email.py |
| Verified By | Reddit, past sessions, user confirmation | Multiple sources confirm |

**GHL Login Credentials (SAVE - NEVER LOSE):**

```
Email: nearmiss1193@gmail.com
Password: Inez11752990@
Location ID: RnK4OjX0oDcqtWw0VyLr
```

**Working Email Webhook (.env - CORRECT):**

```
https://services.leadconnectorhq.com/hooks/uFYcZA7Zk6EcBze5B4oH/webhook-trigger/4ac9b8e9-d444-461d-840b-a14ebf09c4dc
```

**OLD Webhook (reliable_email.py - MAY BE WRONG):**

```
https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/uKaqY2KaULkCeMHM7wmt
```

**Payload Format:**

```json
{
  "email": "recipient@email.com",
  "from_name": "Daniel Coffman",
  "from_email": "owner@aiserviceco.com",
  "subject": "Subject Line",
  "html_body": "<html>...</html>"
}
```

**Reference Files:**

- `reliable_email.py` - Working email sender with webhook
- `send_session_summary.py` - Another working example

---

## 📊 GOOGLE ADS CONVERSION TRACKING (Added Feb 5, 2026 21:24)

| ID | Purpose | Location |
|----|---------|----------|
| G-8080RNWHVV | Google Analytics ID | All pages (in gtag) |
| AW-17858959033 | Google Ads Conversion ID | All pages (in gtag) |
| He5zCNq-qe8bELmt6MNC | Conversion Event Label | thank-you.html only |

**Installed on:** ALL 15 HTML pages in /public
**Conversion fires on:** thank-you.html (post-payment)

---

## 🎯 BOARD-APPROVED SYSTEM PROTOCOLS (Added Feb 5, 2026 19:47)

> [!IMPORTANT]
> **UNANIMOUS BOARD RECOMMENDATION (Claude, Grok, Gemini, ChatGPT)**
>
> These protocols prevent capability loss and session inefficiency.

### Method Priority Hierarchy

| Task | Priority 1 (TRY FIRST) | Priority 2 | Priority 3 (AVOID) |
|------|------------------------|------------|-------------------|
| **Email Sending** | `reliable_email.py` | GHL Webhook | Gmail (app password) |
| **Email Verification** | Hunter.io API | Modal endpoint | Manual lookup |
| **Prospecting** | Modal cloud functions | PageSpeed API | Local scripts |

### When to Run /system_ops

| Timing | Required? | Why |
|--------|-----------|-----|
| **Start of session** | ✅ YES | Fresh rule recall |
| **Before major tasks** | ✅ YES | Pre-task checklist |
| **After failures** | ✅ YES | Check missed rules |
| **After every task** | ❌ NO | Too frequent |

### Pre-Task Checklist (MANDATORY)

Before starting any multi-step task:

- [ ] Confirm all quantities/requirements
- [ ] Check this memory for established methods
- [ ] Verify working directory and file availability
- [ ] State planned approach

### Session Working Commands Log

After successful operations, update `working_commands_log.md`:

```markdown
## [Date] - [Task]
- Method: [what worked]
- Command: [exact syntax]
- Status: ✅ SUCCESS
```

### Progress Confirmation Protocol

After each major step:

1. Confirm completion with specific details
2. State what was done (not what will be done)
3. Ask if user wants to proceed to next step

### Error Recovery Protocol

When a method fails:

1. **STOP** trying variations
2. **CHECK** this memory for proven alternatives
3. **FALLBACK** to Priority 1 method for that task
4. **REPORT** failure before trying alternative

### User Decision Protocol (Added Feb 5, 2026 21:15)

> [!IMPORTANT]
> **When presenting options to the user, follow this protocol:**

| Situation | Action | Example |
|-----------|--------|---------|
| **Quick fix with clear path** | Do it, don't ask | Fix typo, apply board-unanimous feedback |
| **Multiple valid approaches** | Send to Board, present consensus | Template revisions |
| **Time/cost tradeoff** | Ask user preference | Speed vs. thoroughness |
| **Breaking change** | ALWAYS ask first | Delete files, change strategy |
| **Board split decision** | Present to user with synthesis | 2/4 agree vs. 2/4 disagree |

**DEFAULT BEHAVIOR:** If board has clear consensus (3+/4), apply changes without asking.

**NEVER ASK OPTIONS FOR:**

- Board-approved changes (just apply them)
- Fixing obvious errors (just fix them)
- Adding to batch (just research and add)

## 📧 EMAIL BATCH PROTOCOL (Added Feb 5, 2026 20:10)

> [!CAUTION]
> **MANDATORY: Email batches MUST be 10 emails minimum.**
>
> DO NOT send partial batches (3-4 emails) - wastes API calls.

### Workflow (REQUIRED)

| Step | Action | Who |
|------|--------|-----|
| 1 | Generate 10 prospect emails | Agent |
| 2 | Send to Board for review | Agent → Board |
| 3 | Iterate until Board approves | Agent ↔ Board |
| 4 | Present to Dan for final approval | Agent → Dan |
| 5 | Send only after Dan approves | Agent |

### Rules

- **Minimum batch size:** 10 emails
- **Board approval required:** Yes, all 4 AIs
- **Owner approval required:** Yes, after board
- **Partial batches:** ❌ NOT ALLOWED

---

## 📧 EMAIL SENDING PROTOCOL (Updated Feb 5, 2026 16:49)

> [!IMPORTANT]
> **PRIORITY ORDER (Dan's Order - DO NOT CHANGE)**
>
> 1. **Gmail API** - First choice (CONFIGURED ✅)
> 2. **GHL Webhook** - Second choice
> 3. **Resend** - Last resort backup

### Priority 1: Gmail API (FIRST CHOICE) ✅

**Status:** CONFIGURED - Token valid until Feb 5, 2026 21:10

**Script:** `scripts/gmail_api_sender.py`

```python
from scripts.gmail_api_sender import get_gmail_service, send_email, create_bfisher_email

service = get_gmail_service()
email = create_bfisher_email(to_email, business_name, contact_name, website, industry, city)
result = send_email(service, email)
```

**Files:**

- `gmail_credentials.json` - OAuth credentials
- `gmail_token.json` - Active token (auto-refreshes)
- `scripts/gmail_api_sender.py` - Main sender script

### Priority 2: GHL Webhook (SECOND CHOICE)

```python
import requests

GHL_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/uKaqY2KaULkCeMHM7wmt"

payload = {
    "email": "nearmiss1193@gmail.com",
    "from_name": "Daniel Coffman",
    "from_email": "owner@aiserviceco.com",
    "subject": "Subject Here",
    "html_body": "<html>Content</html>"
}
r = requests.post(GHL_EMAIL_WEBHOOK, json=payload)
```

### Priority 3: Resend (LAST RESORT)

```python
from reliable_email import send_email
result = send_email('nearmiss1193@gmail.com', 'Subject', html)
```

### Quick Reference

| Priority | Provider | Status | Script |
|----------|----------|--------|--------|
| 1 | **Gmail API** | ✅ CONFIGURED | scripts/gmail_api_sender.py |
| 2 | GHL Webhook | ✅ Available | reliable_email.py |
| 3 | Resend | ✅ Backup | reliable_email.py |

### Dan's Email

```text
nearmiss1193@gmail.com
```

### Board Recommendations Implemented

| Item | File | Status |
|------|------|--------|
| Working Commands Log | working_commands.log | ✅ Created |
| Pre-Task Checklist | pre_task_checklist.md | ✅ Created |

### Incident Log

| Date | Issue | Root Cause | Fix |
|------|-------|------------|-----|
| Feb 5, 2026 16:51 | Emails sent consolidated | Owner can't preview as customer sees | Send individually with attachments |
| Feb 5, 2026 16:49 | Wrong priority order | Agent changed order without approval | Restored Dan's order |
| Feb 5, 2026 16:18 | Emails not received | Unknown delivery issue | Tested Resend as backup |

---

## 📧 EMAIL APPROVAL WORKFLOW (CRITICAL)

> [!CAUTION]
> **Dan MUST see each email EXACTLY as the customer will receive it:**
>
> - ❌ NO consolidated HTML bundles
> - ❌ NO JavaScript code previews
> - ❌ NO markdown summaries
> - ✅ INDIVIDUAL emails with PDF attachments
> - ✅ Sent to Dan's inbox one-by-one
> - ✅ Identical format the customer will receive

### Approval Process

```text
STEP 1: Create PDFs for each prospect (email_attachments/ folder)
STEP 2: Run: python send_individual_previews.py
STEP 3: Dan receives each email individually with attachment
STEP 4: Dan reviews FROM CUSTOMER PERSPECTIVE
STEP 5: Dan replies: APPROVE / REVISE / REJECT
STEP 6: If APPROVE → Script sends to actual recipients
```

### Script Location

```text
send_individual_previews.py - Sends previews to Dan
```

### Why This Matters

Dan needs to see emails as the CUSTOMER will see them:

- Same subject line
- Same body formatting
- Same PDF attachment
- Same sender signature

---

## 🔍 BOARD EMAIL REVIEW CHECKLIST (MANDATORY - Added Feb 5, 2026)

> [!CAUTION]
> **WHY THIS EXISTS:** Board approved emails without verifying against email_standards.md.
> Emails went to owner missing: traffic light format, PageSpeed screenshots, PDF attachments.
>
> **ROOT CAUSE:** Board was asked "are these good emails?" but NOT "do these match the standard?"

### Before Board Approval, VERIFY Against email_standards.md

| Requirement | Source | Verified? |
|-------------|--------|-----------|
| **PageSpeed PNG screenshot attached** | email_standards.md | [ ] |
| **Mobile view screenshot** (optional) | email_standards.md | [ ] |
| **PDF audit report (2-4 pages)** | email_standards.md | [ ] |
| **Traffic light table in email body** | email_standards.md | [ ] |
| **HTML email format (not plain text)** | email_standards.md | [ ] |
| **Owner name in salutation** | Board consensus | [ ] |
| **Local Florida mention in P.S.** | Board consensus | [ ] |

### Board Review Query Template

```text
Review these email drafts against C:\Users\nearm\.gemini\antigravity\brain\0b97dae9-c5c0-4924-8d97-793b59319985\email_standards.md

VERIFY EACH:
1. Does email have PageSpeed screenshot attached? (REQUIRED)
2. Does email have PDF audit report attached? (REQUIRED)
3. Does email body have traffic light table (🔴🟡🟢)? (REQUIRED)
4. Is email HTML formatted, not plain text? (REQUIRED)
5. Does PDF follow 2-4 page format? (REQUIRED)

Do NOT approve if ANY requirement is missing.
```

### Incident: Feb 5, 2026

| What Happened | Root Cause | Prevention |
|---------------|------------|------------|
| Board approved emails 4/4 | Asked "good emails?" not "match standard?" | Use query template above |
| Owner rejected at preview | Missing: traffic light, PageSpeed, PDF | Verify against email_standards.md |
| 6 emails had to be redone | No checklist verification | This checklist is now mandatory |

---

## 📊 EMAIL TRACKING PIXELS (MANDATORY - Added Feb 5, 2026 18:48)

> [!CAUTION]
> **MANDATORY SOP - NO EXCEPTIONS**
>
> 1. ALL outbound emails MUST contain tracking pixels
> 2. After every 10 emails approved, INFORM OWNER that pixels are in place
> 3. Board MUST verify pixels before final approval
>
> **NEVER send marketing emails without tracking pixels.**

### What Gets Tracked

| Metric | How | Storage |
|--------|-----|---------|
| **Open Rate** | 1x1 transparent pixel image | Supabase `email_opens` |
| **Open Time** | Pixel request timestamp | Supabase `email_opens` |
| **Email ID** | UUID in pixel URL | Links open to contact |
| **IP/Location** | Optional from request | Rough geography |

### Implementation

```html
<!-- Add to bottom of every HTML email body -->
<img src="https://nearmiss1193-afk--ghl-omni-automation-track-email-open.modal.run?eid={EMAIL_UUID}" 
     width="1" height="1" style="display:none;" />
```

### Modal Endpoint Required

```python
@app.function()
@modal.web_endpoint()
def track_email_open(eid: str):
    """Log email open to Supabase"""
    supabase.table("email_opens").insert({
        "email_id": eid,
        "opened_at": datetime.utcnow().isoformat(),
        "ip": get_client_ip()
    }).execute()
    # Return 1x1 transparent pixel
    return Response(content=TRANSPARENT_PIXEL, media_type="image/gif")
```

### Board Verification Checklist

After every 10 emails approved, Board MUST verify:

| Item | Verify How | ✓ |
|------|-----------|---|
| Pixel URL present in HTML | View email source | [ ] |
| Modal endpoint responding | curl endpoint URL | [ ] |
| Supabase table exists | Check email_opens table | [ ] |
| Owner notified | Tag owner with summary | [ ] |

### Notification Template (After Every 10 Emails)

```text
📊 TRACKING PIXEL STATUS

Batch: [Batch Name]
Emails Approved: [X]
Pixels Verified: ✅

Board confirms:
- [ ] Pixel in each email HTML
- [ ] Modal endpoint active
- [ ] Supabase logging configured

Ready to send: [YES/NO]
```

### Why This Exists

Without tracking:

- ❌ No open rate visibility
- ❌ Can't measure campaign success
- ❌ Can't optimize subject lines
- ❌ No engagement data for follow-up

With tracking:

- ✅ Know who opened
- ✅ Know when they opened
- ✅ Can follow up intelligently
- ✅ Measure campaign ROI

---

## 📸 PRIVACY/TERMS EVIDENCE SCREENSHOTS (MANDATORY - Added Feb 5, 2026 19:01)

> [!CAUTION]
> **MANDATORY EVIDENCE COLLECTION**
>
> Before sending ANY email claiming a prospect is missing privacy policy or terms:
>
> 1. Take screenshot of their website footer
> 2. Take screenshot showing absence of privacy/terms links
> 3. Store screenshots internally as evidence
>
> **NEVER claim privacy/terms violation without screenshot proof.**

### Why This Exists

If we claim a business is missing a privacy policy and they actually have one:

- ❌ We look unprofessional
- ❌ We lose credibility
- ❌ Prospect dismisses entire email

### Evidence Collection Process

| Step | Action | Storage Location |
|------|--------|------------------|
| 1 | Screenshot website homepage | `evidence/{business_name}/homepage.png` |
| 2 | Screenshot footer area | `evidence/{business_name}/footer.png` |
| 3 | Search for "Privacy" link | Document if found/not found |
| 4 | Search for "Terms" link | Document if found/not found |
| 5 | Log finding in evidence JSON | `evidence/{business_name}/audit.json` |

### Evidence Folder Structure

```
evidence/
├── Lakeland_AC/
│   ├── homepage.png
│   ├── footer.png
│   ├── audit.json
│   └── timestamp.txt
├── Trimm_Roofing/
│   └── ...
```

### Audit JSON Format

```json
{
  "business": "Lakeland Air Conditioning",
  "website": "thelakelandac.com",
  "audited_at": "2026-02-05T19:01:00",
  "privacy_policy": {
    "found": false,
    "location_checked": ["footer", "homepage", "/privacy"],
    "screenshot": "footer.png"
  },
  "terms_conditions": {
    "found": false,
    "location_checked": ["footer", "homepage", "/terms"],
    "screenshot": "footer.png"
  },
  "notes": "No visible privacy or terms links in footer or homepage"
}
```

### Retention Policy

- **Keep evidence for 2 years minimum**
- **Never delete before contract signed or lead marked dead**
- **Use for legal protection if prospect disputes claims**

---

## 📄 PDF AUDIT REQUIREMENTS (Updated Feb 5, 2026 17:49)

> [!CAUTION]
> **MANDATORY RULES - NO EXCEPTIONS**
>
> 1. Traffic light order: RED top → YELLOW middle → GREEN bottom
> 2. PageSpeed screenshot REQUIRED in PDF
> 3. PDF must contain MORE info than email (otherwise why attach?)
> 4. Privacy = ALWAYS CRITICAL (red)

### Traffic Light Row Order (MANDATORY)

```text
ROW 1: 🔴 CRITICAL (red background)    ← ALWAYS ON TOP
ROW 2: 🟡 WARNING (yellow background)  ← ALWAYS IN MIDDLE  
ROW 3: 🟢 OPPORTUNITY (green background) ← ALWAYS ON BOTTOM
```

**If data doesn't fit this order, REORDER THE ROWS to match this color sequence.**

### PageSpeed Screenshot (REQUIRED)

| Item | Requirement |
|------|-------------|
| **Screenshot** | PageSpeed Insights results page showing actual scores |
| **Format** | PNG embedded in PDF |
| **Shows** | Mobile score, LCP, FCP, CLS, Speed Index |
| **Source** | Captured from pagespeed.web.dev or stored from prior analysis |

### PDF vs Email Content (CRITICAL)

| Content | Email | PDF |
|---------|-------|-----|
| Traffic Light Table | ✅ Summary only | ✅ Full table with details |
| PageSpeed Screenshot | ❌ Never | ✅ REQUIRED |
| Detailed Metrics | ❌ Brief | ✅ Full breakdown |
| Proposed Solutions | ✅ Summary | ✅ Detailed explanation |
| Company/Contact Info | ✅ Brief | ✅ Full cover page |

**The PDF must provide VALUE beyond the email. Email = teaser, PDF = proof.**

### Color Palette for Traffic Lights

```python
# Use these exact colors in reportlab:
RED = colors.HexColor('#dc3545')       # CRITICAL text
LIGHT_RED = colors.HexColor('#f8d7da') # CRITICAL row background
YELLOW = colors.HexColor('#ffc107')    # WARNING text
LIGHT_YELLOW = colors.HexColor('#fff3cd') # WARNING row background
GREEN = colors.HexColor('#28a745')     # OPPORTUNITY text
LIGHT_GREEN = colors.HexColor('#d4edda') # OPPORTUNITY row background
```

### Why Privacy is ALWAYS CRITICAL

1. **Florida Digital Bill of Rights** - Real law, real fines ($50K+)
2. **Creates urgency** - Gives reason to respond
3. **FREE FIX offer** - Our hook to get foot in door
4. **True statement** - Most small business sites ARE non-compliant

### Incidents: Feb 5, 2026

| Time | Issue | Fix Applied |
|------|-------|-------------|
| 17:19 | No traffic light format | Added colored table |
| 17:42 | PDF had no color backgrounds | Added TableStyle BACKGROUND |
| 17:42 | Privacy was WARNING | Changed to CRITICAL always |
| 17:49 | Wrong row order | Fixed to RED→YELLOW→GREEN |
| 17:49 | No PageSpeed screenshot | Added screenshot to PDF |
| 17:49 | PDF same as email | Added more content to PDF |

---

## 🔴 BOARD REVIEW PROTOCOL (MANDATORY)

> [!IMPORTANT]
> **ALL major decisions must go through board review.**
>
> Use `/board_protocol` workflow for strategic decisions.
> Board must verify against BOTH internal logic AND our documented protocols.

### When Board Review is REQUIRED

| Scenario | Required? | Approval Threshold |
|----------|-----------|-------------------|
| Cold email outreach | ✅ YES | **4/4 unanimous** |
| New SOP/process changes | ✅ YES | **4/4 unanimous** |
| Major code changes | ⚠️ RECOMMENDED | 4/4 (or 3/3 if API down) |
| Research synthesis | ⚠️ RECOMMENDED | 4/4 (or 3/3 if API down) |
| Simple clarifications | ❌ NO | N/A |

> **Note:** If an AI API is at its limit/down, then 3/3 of available AIs is acceptable.

### Board Review Workflow

```text
STEP 1: Prepare prompt with context + specific questions
STEP 2: Run python scripts/board_call_raw.py
STEP 3: Synthesize 4 AI responses (Claude, Grok, Gemini, ChatGPT)
STEP 4: If 3/4 APPROVE → Proceed to owner approval
STEP 5: If REVISE → Apply changes and resubmit
STEP 6: If REJECT → Start over
```

### Board Prompt Template

```text
BOARD REVIEW: [Topic]

## CONTEXT
[Situation and background]

## PROPOSED ACTION
[What we want to do]

## QUESTIONS FOR BOARD
1. [Specific question 1]
2. [Specific question 2]
...

## VERIFY AGAINST
- Internal logic (does this make sense?)
- Our documented protocols in operational_memory.md
- Past incidents and lessons learned

## EXPECTED OUTPUT
- APPROVE / REVISE / REJECT for each question
- Specific recommendations if REVISE
- Final vote
```

### Past Board Decisions (Reference)

| Date | Topic | Vote | Key Decision |
|------|-------|------|--------------|
| Feb 5, 2026 | Email verification process | 4/4 YES | Use 6-step verification sequence |
| Feb 5, 2026 | Email format revisions | 3/4 YES | Use text labels, owner names, bullet format |

## 🔴 MANDATORY: EMAIL VERIFICATION BEFORE SENDING (Feb 5, 2026)

> [!CAUTION]
> **NEVER GUESS EMAIL ADDRESSES**
>
> On Feb 5, 2026: 6/10 emails bounced because agent guessed `info@`, `contact@`, `service@` formats.
>
> **RULE: Use `/email_outreach` workflow for ALL email sends.**

### Email Verification Sequence (MANDATORY)

| Step | Tool | Action |
|------|------|--------|
| 1 | Hunter.io API | Search domain for contacts |
| 2 | Apollo.io API | Search company for decision-makers |
| 3 | Company Website | Check Contact/About/Team pages |
| 4 | LinkedIn Search | Find owner/manager profiles |
| 5 | Google Search | "[Company] [City] FL owner email" |
| 6 | `search_web` | Web search for verified contact |

**If ALL fail:** Add to Manus batch list, DO NOT GUESS.

### Workflow Slash Command

Invoke `/email_outreach` before any cold email task. This enforces:

- ✅ Research each email before sending
- ✅ Document source of each verified email
- ✅ Get owner approval before sending
- ✅ Check for bounces after sending

### Complete Email Workflow (MANDATORY)

```
STEP 1: RESEARCH
└── Verify email addresses (Hunter → Apollo → Website → LinkedIn → Google → search_web)
└── Find owner/contact names
└── Document sources

STEP 2: DRAFT
└── Use proven B&W template format
└── Include PageSpeed data if available
└── Attach PDF audit report

STEP 3: BOARD REVIEW
└── Run drafts through /board_protocol
└── Get 4 AI responses (Claude, Grok, Gemini, ChatGPT)
└── Synthesize recommendations

STEP 4: BOARD APPROVAL
└── All 4 AIs must vote APPROVE or majority (3/4)
└── If REVISE: Make changes and resubmit
└── If REJECT: Do not proceed

STEP 5: OWNER APPROVAL (EMAIL REQUIRED)
└── EMAIL drafts to Dan (nearmiss1193@gmail.com)
└── Include all email content in one consolidated email
└── Subject: "APPROVAL REQUESTED: [X] Email Drafts"
└── Wait for reply: APPROVE / REVISE / REJECT
└── If changes requested: Go back to Step 2

STEP 6: SEND
└── Only after owner APPROVES via email reply
└── Send via Gmail API or GHL webhook
└── Verify no bounces within 30 min
```

> [!IMPORTANT]
> **Owner approval = EMAIL to Dan, not just showing in artifact.**
> Dan must receive and reply to an email before sending outreach.

---

## 🔴 EMAIL OUTREACH SOP V2 – BOARD APPROVED (Feb 5, 2026)

> **AUTHORITY**: 4/4 Board Vote (Claude, Grok, Gemini, ChatGPT all YES)

### Issue 1: Contact Name Research (MANDATORY)

**NEVER send to "Dear Team"** - Find actual contact names first.

**Research Order (Exhaustive):**

1. **LinkedIn Sales Navigator** - Search by company name for owner/manager
2. **Hunter.io/Apollo.io** - Domain search for decision-makers
3. **Company Website** - "About Us" / "Team" / "Contact" pages
4. **Google Search** - "[Business Name] [City] FL owner"
5. **BBB Listings** - Business registration records
6. **Industry Directories** - Trade associations

**Fallback (Last Resort):** "Dear Business Owner" - NOT "Dear Team"

**Time Limit:** 10 minutes per business. If nothing found → Manus batch list.

### Issue 2: Comprehensive PDF Audit Structure

**Current (Too Basic):** Only repeats email content.

**New Structure (Board-Approved):**

```
PAGE 1: COVER + EXECUTIVE SUMMARY
- Company name, date, personalized greeting
- Key findings overview

PAGE 2: CURRENT PROBLEMS
- Issues hurting their business NOW
- Future risks they should be aware of
- Basic competition analysis (2-3 competitors)

PAGE 3: INTERNAL OFFICE SYSTEMS
- Dispatch management
- Payroll handling
- Company newsletters for customer retention

PAGE 4: DIGITAL MARKETING SERVICES
- Google Business Profile upgrades + monitoring
- Facebook management
- Instagram management
- Online reputation management

PAGE 5: CUSTOMER RETENTION STRATEGIES
- Newsletter program for referrals
- First-name recognition benefits
- Referral program setup
- Customer lifetime value improvement

PAGE 6: NEXT STEPS + CTA
- Service packages (Basic/Premium/Complete)
- Case study examples
- Contact information
```

### Issue 3: Additional Services to Mention

**Internal Systems:**

- ✅ Dispatch management
- ✅ Payroll handling
- ✅ Company newsletters

**Digital Marketing:**

- ✅ Google Business Profile
- ✅ Facebook management
- ✅ Instagram management

**Customer Retention:**

- ✅ Newsletter → referrals → first-name recognition
- ✅ Long-term engagement strategies
- ✅ Customer lifetime value focus

---

## Feb 5, 2026: Prospecting Workflow & Contact Research

### PROSPECTING BATCHING PROTOCOL (MANDATORY)

| Batch Type | Trigger | Action |
|------------|---------|--------|
| **Ready for Outreach** | 10 prospects with owner/contact info | Send emails to Dan for approval |
| **Missing Contacts** | 30 prospects without owner info | Compile list + Manus prompt + failed tactics |

### Contact Research Order (Exhaustive)

1. **Hunter.io API** - Search by domain for decision-makers
2. **Web Search** - "[Business Name] [City] FL owner"
3. **LinkedIn Search** - "[Business Name] LinkedIn"
4. **Domain Variations** - Try "firstname@domain" patterns
5. **If ALL fail** → Add to Manus batch list

### Failed Tactics to Report (Feb 5, 2026)

When compiling Manus list, include these failed tactics:

- Hunter.io API: Works for some, returns empty for many local businesses
- Google Search: "[Business] owner" - Works for larger companies, fails for small local
- Franchise businesses: Owner info not public (e.g., Honest 1 Auto Care)

### Manus Prompt Template

```
Find the owner or primary decision-maker for these 30 businesses:

[LIST OF BUSINESSES WITH:
- Business Name
- Website/Domain
- City, State
- Industry]

For each business, return:
- Owner/Contact Name
- Title/Role
- Email (if available)
- Source where found

Search tactics to try:
1. Business registration records
2. LinkedIn company pages
3. Local news/press releases
4. BBB listings
5. Industry directories
```

### GitHub Watchdog Status

- **Issue**: System Watchdog was failing (Railway endpoint not responding)
- **Status**: RESOLVED (Railway returning 200 OK as of Feb 5, 2026)
- **Cause**: Transient - Railway cold start or temporary network issue
- **Action**: No fix needed - endpoint is healthy

### Board Analysis Summary (Feb 5, 2026)

Dual-transcript analysis completed (Nick Ponty AEO + Jack Roberts AntiGravity):

**Validated Tactics:**

- AEO pricing $500-$3K/month ✅
- Trust Audits via High Level ✅
- Soft-sell email templates ✅
- GBP 16-point optimization ✅
- Target $500K-$2M revenue businesses ✅

**Tools to Invest In:**

- Manis AI ($30/month) - Already have subscription ✅
- Zapier/High Level - For automation
- Firecrawl - For competitor research

**Dismissed as Hype:**

- Apple/Google Siri partnership claims ❌
- "30-minute 6-figure apps" ❌
- Google "Guided Learning" ❌

---

## Jan 30: Sovereign 2.0 Hardening

- **Architecture Split**:
  - `nexus-engine`: Dedicated to crons and outreach workers. Stable, high-priority.
  - `nexus-portal`: Dedicated to webhooks, landing pages, and the secured dashboard.
- **Security Lockdown**:
  - Dashboard moved to `sov_8k2_cmd.html`.
  - `robots.txt` disallows dashboard indexing.
  - Local Key: `empire_2026` required for dashboard persistence.

## System Status: ABSOLUTE READY

- [x] **ABSOLUTE READY – Verification Scripts Permanently Disabled Per Executive Order**
- [x] **ZERO SCRIPT VERIFICATION MODE ACTIVE** (Never run Python/Subprocess in verification)
- [x] **ZERO NETWORK MODE ACTIVE** (Prevent all REPL hangs)

### Lock-Down Rules (ULTIMATE KILL SWITCH)

- **Never use `python -c`, `subprocess`, `requests`, or any external/network call.**
- **NEVER run any Python script, subprocess, or external call in verification steps.**
- All status checks are manual or string-based only.
- All bridge/notification calls replaced with internal file writes.
- Use only pure Python string/file operations.
- Lock-down token: `sov-audit-2026-ghost`
- All 10s recovery timeouts enforced.
- **Phase 3: Persistent Wisdom (Context Loop)**:
  - `system_wisdom`: New schema to store cross-lead insights and patterns.
  - `wisdom_engine.py`: Daily background worker synthesizes successful interactions into high-level wisdom.
  - Research Injection: `research_lead_logic` now fetches lead history and system wisdom to draft context-aware hooks.
- **Micro-App Image Optimization**:
  - Replaced monolithic module mounting with selective `add_local` calls in `core/image_config.py`.
  - Purged 70,000+ legacy files from the Modal build environment, reducing image size by ~1.3GB.
- **Phase 4: Mission Alignment (ROI Metrics)**:
  - Financial Layer: Added `deal_value` support to `contacts_master` (default $497).
  - Business Attribution: Implemented auto-calculation of **Pipeline Value** and **Outreach Burn** in `api/webhooks.py`.
  - Burn Estimation: $0.15/min for calls, $0.01 for SMS/Emails.
  - Command UI: ROI Stats panel replaced legacy "Traffic Sources".
- **Master Prompt v5.5**: Active with Evolution and Sentinel protocols.

---

### Jan 29 Early Morning - Outreach Hardening (Rule #1)

**Completed:**

- ✅ **Vapi Native Integration**: Switched to verified native ID `8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e` for `+18632132505`. Resolved "error-get-transport" 400.
- ✅ **GHL DND Pre-flight**: Added DND checks in `workers/outreach.py` for SMS to prevent false success.
- ✅ **Rule #1 Enforcement**: Updated `workers/outreach.py` to only report success when database records are created.
- ✅ **Vapi Webhook Persistence**: Updated `api/webhooks.py` to store live call events (types) in `outbound_touches`.
- ✅ **Cloud Sync**: Fixed `deploy.py` internal function call syntax (use `.local()` for within-app logic).

**Key Learnings:**

- **Vapi Carrier Trust**: Native Vapi numbers (provisioned in-dashboard) avoid 400 transport errors that Twilio-imported numbers sometimes hitting in specific regions.
- **Rule #1 (Actual Delivery)**: Never trust an API "201 Created" alone. Success is only verified when the database reflects the touch.
- **Modal Internal Calls**: When calling another `@app.function` within the same Modal app, use `func.local()` to execute logic without re-serializing.
- **Business Hours Bypass**: For late-night verification, temporary bypass of `is_business_hours()` is required to trigger pulses.

---

### Jan 27 - Modal App Alignment & SMS Relay Fix

**Completed:**

- ✅ **Modal App Name Re-alignment**: Switched app name from `ghl-omni-automation` back to legacy `empire-api-v3` to match GHL's hardcoded webhooks.
- ✅ **SMS Inbound Relay**: Restored `/api/sms/reply-text` and `/api/sms/reply-sent` endpoints in `deploy.py` to handle GHL's "Inbound SMS Webhook Relay".
- ✅ **Sarah AI SMS Integration**: Added Gemini-powered responder logic to the legacy SMS relay endpoint.
- ✅ **Internal Import Stabilization**: Fixed serialization errors in Modal by moving `get_supabase` imports inside all worker functions.

**Key Learnings:**

- **Legacy Dependencies**: External systems (GHL) often have hardcoded webhook URLs. Restoring the old Modal URL (`empire-api-v3`) is faster than updating dozens of GHL automation steps.
- **Modal Serialization**: `@app.function` workers MUST have `from modules... import ...` INSIDE the function body if the module is mounted/added via `add_local_dir`.
- **Campaign Mode**: The system uses `system_state` key `campaign_mode` set to `working` (active) or `broken` (manual kill switch).

---

### Jan 23 - Analytics & Tracking System

**Completed:**

- ✅ Backend: Created `/api/track` endpoint in `deploy.py` (FastAPI) to capture pageviews and clicks.
- ✅ Database: Events stored in `web_events` Supabase table.
- ✅ Frontend: Created `tracker.js` with session logic and click listeners.
- ✅ UX: `tracker.js` shows **Green Border** on success / **Red Border** on failure for easy debugging.
- ✅ Accessibility: Fixed `alf_landing.html` lint errors.

**Key Learnings:**

- **Modal Static Files:** Must explicitly `mount` the `/public` directory in `deploy.py` to serve relative assets like `tracker.js`.
- **FastAPI Imports:** `func.wsgi_app()` inside Modal can lose top-level imports; re-import `FastAPI`, `StaticFiles`, etc. inside the function.
- **Supabase Env Vars:** `NEXT_PUBLIC_SUPABASE_URL` is the correct key in this environment, not just `SUPABASE_URL`.

---

### Jan 15 - Premium Audit Reports & GHL Chat Widget

**Completed:**

- ✅ `premium_audit_generator.py` - Chart.js charts, score circles, animations, voice+chat widgets
- ✅ `turbo_manus.py` - Campaign runner for audits + email + SMS + calls (10 min loop)
- ✅ GHL Chat Widget added to 23 public HTML pages (widget ID: `69507213261ca136120c2fe0`)
- ✅ Vapi Voice Widget added to audit report pages
- ✅ Outbound Calls VERIFIED (Vapi 201 response)
- ✅ Outbound SMS VERIFIED (GHL webhook)
- ✅ Phone validation - US-only filtering, reject Canadian/fake numbers

**GHL Inbound SMS Workflow Created:**

- **Trigger:** Customer Replied → SMS channel
- **Action:** Webhook POST to `https://empire-unified-backup-production.up.railway.app/ghl/inbound-sms`
- **Payload:** contactId, phone, email, message
- **Status**: ✅ Published and tested via `test_railway_sms.py`

---

### Jan 15 Evening - Manus Import & Deployment

**Completed:**

- ✅ Scraped 290 HVAC leads from Manus share link
- ✅ `import_manus_leads.py`: Imported 290 leads to Supabase (Schema fix: removed `contact_name` which was missing from DB)
- ✅ `railway/app.py`: Sarah SMS fix. Changed model from `gemini-1.5-flash` to `gemini-2.0-flash` (fixed 404 API error on Railway)
- ✅ `modal_turbo_manus.py`: Deployed turbo manus campaign to Modal Cloud for 24/7 operation (optimized with logic to skip `node_modules`)
- ✅ `turbo_manus.py`: Fixed Windows encoding errors and replaced emojis with ASCII for console stability

**Key Learnings:**

- **Gemini API (Early 2026)**: `gemini-1.5-flash` returning 404 on `v1beta`/`v1`. `gemini-2.0-flash` is the stable replacement.
- **Supabase Schema**: `leads` table does NOT have `contact_name`. Use `company_name` as unique identifier.
- **Modal Deployment**: Use `ignore` in `add_local_dir` to avoid 10k+ file uploads from `node_modules`.

---

### Jan 15 Night - Vapi International Call Error (Verified Jan 15, 2026)

**Sources:**

- [Vapi Docs: Call Ended Reasons](https://docs.vapi.ai/calls/call-ended-reason)
- [Vapi Docs: Outbound Calling](https://docs.vapi.ai/phone-calling/outbound-calls)

**Root Cause:** All outbound calls failing with `call.start.error-vapi-number-international`

**Cross-Reference Table:**

| Aspect | Source 1 (Vapi Docs) | Source 2 (Community) | Match? |
| :--- | :--- | :--- | :--- |
| Error Meaning | Free Vapi# can't call international | Free Vapi numbers are US-only | ✅ |
| Target Number | +1 (250) = British Columbia, Canada | Canadian numbers are international | ✅ |
| Fix | Import Twilio# OR filter international | Use Twilio-imported number | ✅ |

**Key Findings:**

- FREE Vapi phone numbers (like +1 863 213 2505) can ONLY call US domestic numbers
- +1 (250) is a CANADIAN area code (British Columbia) - treated as international
- Solution: Filter out non-US numbers from outreach, OR import Twilio number w/ international enabled

---

### Jan 14 - Railway Schema Fix & Resend Webhooks

**Completed:**

- ✅ Identified TWO Railway projects: `zesty-curiosity` (main) and `zonal-exploration`
- ✅ Fixed `zonal-exploration` ImportError - added `supabase`, `python-dotenv`, `schedule` to requirements.txt
- ✅ Fixed schema error - code queried non-existent `leads.state` and `leads.phone` columns
- ✅ Added email fallback - if Lusha fails, generate `info@domain` from website
- ✅ Added auto-restart mechanism - `/health` restarts scheduler if heartbeat >5 min
- ✅ Added `/stats` endpoint for live metrics
- ✅ Website compliance - updated for Google Startup Credit criteria

**Key Learnings:**

- GHL email delivery blocked/slow - Resend is primary reliable sender
- Resend webhooks: `email.opened`, `email.clicked` events
- Use `tags` in Resend API for lead correlation

---

### Jan 13 - Apollo Fix & EmpireBrain Integration

**Completed:**

- ✅ Rachel upgraded: GPT-3.5 → GPT-4, dynamic personality
- ✅ 14-Day Free Trial fixed everywhere
- ✅ Owner email copy enabled (BCC to <owner@aiserviceco.com>)
- ✅ GHL Email Webhook created
- ✅ EmpireBrain integrated into Railway

**Key Learnings:**

- **Apollo API:** Use `v1/organizations/search` (NOT `mixed_companies`). Auth via `X-Api-Key` header.
- **Railway Env Vars:** Set manually via Dashboard > Variables > Raw Editor
- **Supabase Fix:** Code expected `SUPABASE_URL`/`SUPABASE_KEY` but vars are `NEXT_PUBLIC_SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY`
- **Analytics Modules Created:** `lead_scorer.py`, `pipeline_analytics.py`, `ab_test_tracker.py`
- **Lusha Enrichment:** Uses `X-Api-Key` header for direct dial phone/email

---

### Jan 15 Morning - GHL SMS Debug

**Issue:** Railway/Supabase errors
**Root Cause:** Two Supabase projects exist - `zlswdojxsngkketnfvow` (wrong) and `rzcpfwkygdvoshtwxncs` (correct)
**Fix:** Updated Railway env vars to correct project

**Additional Learnings:**

- `memory.py` vs `app.py` - both need same Supabase credentials
- PGRST204 Error = column doesn't exist OR schema cache stale
- Fix: ADD COLUMN + `NOTIFY pgrst, 'reload schema'`
- Always check Railway logs after deploy - build success ≠ runtime success

---

## Verified Configurations

### Vapi Voice Widget

```javascript
VAPI_PUBLIC_KEY = "3b065ff0-a721-4b66-8255-30b6b8d6daab"
ASSISTANT_ID = "1a797f12-e2dd-4f7f-b2c5-08c38c74859a" // Sarah 3.0
```

### GHL Chat Widget

```html
<script
  src="https://beta.leadconnectorhq.com/loader.js"
  data-resources-url="https://beta.leadconnectorhq.com/chat-widget/loader.js"
  data-widget-id="69507213261ca136120c2fe0">
</script>
```

### GHL Webhooks

- **SMS:** `https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd`
- **Email:** `https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8`

### Railway Endpoints

- **Health:** `https://empire-unified-backup-production.up.railway.app/health`
- **Stats:** `https://empire-unified-backup-production.up.railway.app/stats`
- **Inbound SMS:** `https://empire-unified-backup-production.up.railway.app/ghl/inbound-sms`
- **Vapi Webhook:** `https://empire-unified-backup-production.up.railway.app/vapi/webhook`
- **Resend Webhook:** `https://empire-unified-backup-production.up.railway.app/resend/webhook`

---

## System Capabilities Summary

### Sarah AI Channels

| Channel | Inbound | Outbound |
| :--- | :--- | :--- |
| Voice Calls | ✅ Vapi auto-answers | ✅ turbo_contact.py |
| SMS | ⏳ Needs GHL publish | ✅ GHL webhook |
| Chat Widget | ✅ GHL widget | N/A |
| Voice Widget | ✅ All pages | N/A |

### Outreach Capabilities

- ✅ Email via GHL/Resend webhooks
- ✅ SMS via GHL webhooks
- ✅ Calls via Vapi API
- ✅ Premium audit reports (self-hosted with Chart.js)

---

## Key Scripts Reference

| Script | Purpose |
| ------ | ------- |
| `premium_audit_generator.py` | Generate HTML reports with Chart.js, voice+chat widgets |
| `turbo_manus.py` | Campaign runner: audits + email + SMS + calls (10 min loop) |
| `turbo_contact.py` | Direct outbound calls to leads |
| `turbo_prospect.py` | Prospect HVAC leads from Apollo |
| `continuous_swarm.py` | Main campaign swarm - prospect + outreach + calls |
| `check_vapi.py` | Debug Vapi phone/assistant configs |
| `import_manus_leads.py` | Import leads from Manus CSV |

---

## Recovery Commands

```bash
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified

# Manus-style campaign (audits + email + SMS + calls)
python turbo_manus.py

# Standard continuous swarm
python continuous_swarm.py

# Direct outbound calls
python turbo_contact.py
```

---

## Architecture Overview

| Component | Platform | URL/Endpoint |
| --------- | -------- | ------------ |
| Backend Worker | Railway | `empire-unified-backup-production.up.railway.app` |
| Website/Dashboard | Squarespace + Static HTML | `https://aiserviceco.com` |
| Database | Supabase (PostgreSQL) | `rzcpfwkygdvoshtwxncs.supabase.co` |
| Voice AI | Vapi.ai | `api.vapi.ai` |
| CRM/Workflows | GoHighLevel (GHL) | `app.gohighlevel.com` |
| Email (Primary) | Resend | `api.resend.com` |

---

## Key Numbers & Contacts

| Item | Value |
| ---- | ----- |
| Main Phone | (352) 758-5336 |
| Sarah Assistant ID | 1a797f12-e2dd-4f7f-b2c5-08c38c74859a |
| Rachel Assistant ID | 033ec1d3-e17d-4611-a497-b47cab1fdb4e |
| Vapi Phone ID | 8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e |
| Trial Period | **14-Day Free Trial** |
| Pricing | $297 / $497 / $997 |
| Owner Email | <nearmiss1193@gmail.com> |
| Business Email | <owner@aiserviceco.com> |

### [Jan 29, 2026] Redundant Interpolation Method

**Problem**: GHL sent literal `(reply_text)` because the webhook payload key `replyText` did not match the expected `message` or `reply_text` in certain workflows.
**Solution**: Standardized `railway/app.py` to send a triple-redundant payload:

```json
{
  "message": reply_text,
  "reply_text": reply_text,
  "replyText": reply_text
}
```

**Status**: Permanent memory archived. Rule #1 of GHL Dispatches defined.

---

## BOARD LOCK V1 – EXECUTIVE ORDER (Feb 4, 2026)

### ⚫ NO FAKE CALLS RULE

For every board meeting or external AI request, Antigravity MUST:

1. **Print the actual curl command** it ran (or equivalent API call)
2. **Print the exact response** (headers + body)
3. **If response is missing or fake** → Log `HALLUCINATION DETECTED` and **STOP**

No summaries, no "thinking" – just raw output.

---

### ⚫ BOARD CONSENSUS LOCK – PERMANENT

Before ANY `execute`, `deploy`, `send`, or major change:

1. **Run a board call**: "Should we [action]?"
2. **Ask all four**: Claude, Grok, Gemini, ChatGPT
3. **Print raw curl command + response** for each
4. **Require 3/4 YES votes** to proceed
5. **If under 3/4 or any call fails** → Log `BLOCKED – NO CONSENSUS` and **STOP**

**NO EXCEPTIONS. NO SKIPPING.**

---

### Board Call Implementation

**Script**: `scripts/cross_ai_board.py` (General system audit)  
**Script**: `scripts/website_board_meeting.py` (Website-specific)

**Threshold**: 3/4 = 75% approval required  
**Quorum**: Minimum 3 AIs must respond  
**Tie-breaker**: User decides if 2/2 split with 2 failures

---

### API Keys (Locked for Board Calls)

| AI | Key Variable | Status |
|----|--------------|--------|
| Claude | `ANTHROPIC_API_KEY` | ✅ Active |
| Grok | `GROK_API_KEY` | ✅ Active |
| Gemini | `GEMINI_API_KEY` | ✅ Active |
| ChatGPT | `OPENAI_API_KEY` | ✅ Active |

---

**LOCK STATUS**: 🔒 **PERMANENTLY LOCKED**  
**Effective**: February 4, 2026  
**Authority**: Executive Order by Dan (Founder)

---

## BOARD OVERRIDE V2 – EXECUTIVE ORDER (Feb 4, 2026)

### ⚫ NO SELF-FIX RULE

When user says **"board call"** on any topic:

1. **STOP ALL INTERNAL LOGIC** – No diagnosis, no code review, no thinking
2. **ONLY call the real APIs** – Print the curl command + raw response
3. **DO NOT diagnose** – No root cause analysis
4. **DO NOT fix** – No code changes
5. **DO NOT summarize** – Only raw API output
6. **If ANY AI call fails** → Log `BOARD FAILED` and **STOP**

**NO EXCEPTIONS.**

---

### Execution Flow for "board call"

```
USER: "board call on [topic]"

→ Antigravity runs: python scripts/cross_ai_board.py
→ Prints: curl command for each AI
→ Prints: raw response body for each AI
→ NO analysis
→ NO recommendations
→ STOP
```

---

**LOCK STATUS**: 🔒 **PERMANENTLY LOCKED**  
**Effective**: February 4, 2026  
**Authority**: Executive Order by Dan (Founder)

---

## 🔴 PUSH OR DIE PROTOCOL (Feb 4, 2026)

> **NEVER skip git push.** If push fails, abort deploy immediately and log 'PUSH FAILED - DEPLOY ABORTED'. This is FATAL. No bypass. No partial deploy.

### Rules

1. `git push --force` is MANDATORY before any deploy
2. If push fails → abort immediately, log error, exit 1
3. No deploy without successful push
4. Both Netlify and Vercel deploys require push first

**SAVE PROTOCOL locked – push is now fatal. No more skipping.**

---

## 🧠 SOVEREIGN MEMORY SYSTEM (Feb 4, 2026)

### HARD RULES - QUERY BEFORE ACTION

1. **BEFORE editing ANY embed, form, or widget code** → Query `system_state` for config keys starting with `ghl_` or `vapi_`
2. **BEFORE ANY code edit** → Query for similar patterns in saved code
3. **ON ANY error** → Query for known solutions before debugging from scratch
4. **ALWAYS save working code** → After successful fix, save to memory
5. **NEVER rely on AI memory** → Always verify against Supabase

### Critical Config (NEVER CHANGE WITHOUT VERIFICATION)

| Key | Value | Domain |
|-----|-------|--------|
| ghl_form_id | 7TTJ1CUAFjhON69ZsOZK | links.aiserviceco.com |
| ghl_calendar_id | YWQcHuXXznQEQa7LAWeB | links.aiserviceco.com |
| vapi_public_key | 3b065ff0-a721-4b66-8255-30b6b8d6daab | - |
| vapi_assistant_id | 1a797f12-e2dd-4f7f-b2c5-08c38c74859a | - |
| vapi_widget_title | Talk to Sales | - |
| vapi_widget_color | #f59e0b | Yellow/orange |

### WRONG VALUES - NEVER USE

- ❌ `RnK4OjX0oDcqtWw0VyLr` (wrong form ID)
- ❌ `M7YwDClf34RsNhPQfhS7` (wrong calendar ID)
- ❌ `api.leadconnectorhq.com` (wrong domain)
- ❌ `link.msgsndr.com` (wrong domain)
- ❌ `calendar.gohighlevel.com` (wrong domain)

### Supabase Tables (Pending Creation in Dashboard)

Run `create_sovereign_tables.sql` in Supabase SQL Editor to create:

- sovereign_config
- sovereign_actions
- sovereign_errors
- sovereign_code
- sovereign_preferences
- sovereign_tasks
- sovereign_embeddings
- sovereign_sessions
- sovereign_logs
- sovereign_alerts

---
