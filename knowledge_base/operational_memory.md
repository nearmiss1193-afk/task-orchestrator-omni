# 🧠 SOVEREIGN OPERATIONAL MEMORY

## Behavioral & Tactical Wisdom (Feb 2026)

---

## 🚨 CRITICAL RULE: EMAIL OUTREACH WORKFLOW (Feb 5, 2026)

> [!CAUTION]
> **NEVER SKIP THIS WORKFLOW. NEVER SHOW EMAILS TO OWNER BEFORE BOARD APPROVAL.**

```
1. PROSPECT      → Always prospecting, collect 10+ with real data
2. REAL DATA     → Run ACTUAL PageSpeed tests (NO HALLUCINATIONS)
3. EMAIL DRAFTS  → bfisher format with REAL metrics only
4. BOARD REVIEW  → Submit to Claude/Grok/Gemini FIRST
5. OWNER REVIEW  → AFTER board approves, show to Dan
6. SEND          → Gmail API only after Dan approves
```

**MISTAKES MADE (Don't Repeat):**

- Sent test email before board approval ❌
- Used spammy HTML template instead of bfisher plain text ❌
- Missing PDF audit attachment ❌

---

## 🏛️ SECTION 1: USER-CENTRIC PROTOCOLS

### ⚖️ The "Speak-Before-Fix" Mandate

- **Rule**: If the user requests an update, explanation, or "tell me what happened," the agent MUST stop all background technical activities immediately.
- **Priority**: Communication > Execution.
- **Learning**: Neglecting to explain a technical loop creates user frustration and appears as "system failure" even if the agent is working hard.

---

## 🏛️ SECTION 2: THE DELEGATION & LOOP STABILITY PROTOCOL (SDLSP)

### 🧩 Core Architecture

The system operates on an "Architect-Worker" model.

1. **The Sovereign Architect (Primary Agent)**:
   - **Role**: Maintains the chat line with the user.
   - **Protocol**: NEVER lock the chat context for long-running technical tasks (deployments, large migrations, complex debugging).
   - **Delegation**: Spawns a `browser_subagent` or a `background_command` for any task estimated to take >10 seconds.

2. **The Execution Worker (Sub-Agent)**:
   - **Role**: Executes technical tasks in a sandbox or isolated context.
   - **Protocol**: Reports progress every 30 seconds to the Architect.

### 🔄 Loop Detection & Intervention

This is the "Safety Valve" to prevent system paralysis.

- **Pulse Check**: The Architect must monitor the "Worker" pulse every minute.
- **Anomaly Detection**: If a Worker repeats the same command 2 times without a state change (e.g., getting the same syntax error or 404), the Architect MUST intervene.
- **The Intervention Protocol**:
   1. **Pause Worker**: Terminate the looping process immediately.
   2. **Status Report**: Notify the user IMMEDIATELY: *"I've detected a loop in the [Sub-Agent Name]. It is stuck on [Specific Error]."*
   3. **Forensic Research**: The Architect must conduct research into the root cause.
   4. **Board Consultation (MANDATORY)**: Before attempting a 3rd time, the error/discovery MUST be summarized and presented for external audit. The "Sovereign Board" includes:
      - **Grok** (X/Intelligence)
      - **ChatGPT** (OpenAI/Logic)
      - **Claude** (Anthropic/Strategy)
      - **Gemini** (Google/Data - via External Audit Bridge)
   5. **Board Approval**: Only proceed with a fix once the user reports the Board's consensus or provides a direct strategic pivot.

---

## 🏛️ SECTION 4: SYSTEM STATE & VAULT (Feb 2026)

### 🔑 Definitive Credentials (Verified)

- **Token**: `sov-audit-2026-ghost` (Internal Sovereign Handshake)
- **GHL Agency Token**: `managed_by_vault` (Production PIT - See Vault)
- **GHL Location ID**: `RnK4OjX0oDcqtWw0VyLr` (Verified Primary Location)
- **xAI/Grok Key**: `managed_by_vault` (Grok Modern Context - See Vault)

### 📊 Strike Results (Phase 4.3)

- **Handshake**: Verified 615 leads available in the production funnel.
- **Outreach**: GHL Webhook bridge (`RnK4Oj.../uKaqY2...`) is the high-reliability path.
- **Grok Modern Context**: 'Daniel reclaim ROI for Lakeland businesses. Focus on simple 5th-grade language, "rescue" pitches, Sarah AI for leads.'

## 🏛️ SECTION 5: 7-DAY SOVEREIGN INCOME PROTOCOL (Default SOP)

**Directive**: This is the default operational rhythm until further notice.

### 📅 The Weekly Strike Cycle

- **Day 1: Research**
  - Goal: Generate 20 high-quality leads (Roofing/Law/HVAC/Spas).
  - Protocol: Search Google Pages 2-3 for "Trust Killers" (Broken SSL, slow speed, no privacy).
  - Cross-check with 2+ external AIs (ChatGPT/Claude).
- **Day 2: Prep**
  - Goal: Create 10 personalized "Traffic Light" reports and call scripts.
  - Validation: Use Grok to simplify hooks and verify technical issues.
- **Day 3: Outreach**
  - Goal: Send 5-10 personalized "Rescue" emails (5th-grade level).
  - Action: Follow up with a call 1 hour later. Log all activity.
- **Day 4: Follow Up**
  - Goal: Retarget rejects with screenshots and "Competitive Edge" data (Reclaiming market gaps).
- **Day 5: Close**
  - Goal: Demo free patches and upsell Sarah AI ($1,500/month). Track wins.
- **Day 6: Review**
  - Goal: Analyze response rates and add 10 new warm leads.
- **Day 7: Scale**
  - Goal: Automate sourcing/sending.
  - Report: Deliver 4:30 PM EST CSV and 5:00 PM EST Summary to Daniel.

### ✍️ Communication Standards

- **Readability**: Always 5th-grade level (Short sentences, zero jargon).
- **Verification**: 20% manual verification + multi-AI cross-check (ChatGPT/Claude/Grok).
- **Frequency**: 10-minute throttling between outreach sends.

---

## 🏛️ SECTION 6: SESSION LEARNINGS (Feb 4, 2026)

### 🚦 Traffic Light Audit Email (Board Consensus)

**Format:** RED → YELLOW → GREEN for prospect emails

| Color | Meaning | Threshold |
|-------|---------|-----------|
| 🔴 RED | Critical (Fix NOW) | PageSpeed <50, Load >5s |
| 🟡 YELLOW | Warning (Fix Soon) | PageSpeed 50-74, Load 3-5s |
| 🟢 GREEN | Good (Keep Up) | PageSpeed 75+, Load <3s |

**Order:** RED first (urgency) → YELLOW (concern) → GREEN last (rapport)

### 📧 Prospecting Sequence (Board Adjusted)

| Step | Timing |
|------|--------|
| Email | Day 1 |
| SMS | Day 3 (NOT 1 hour later) |
| Call | Day 5 |

**Key:** 24-48 hours between touches, not 1 hour

### 🛠️ Prospecting Toolkit

- Google Maps (find prospects)
- LLMs (research websites)
- PageSpeed screenshots (performance hook)
- GHL Style Audits (CRM hook - needs Playwright/Puppeteer)
- LinkedIn/Reviews (find names)
- Gemini (create personalized docs)

### 📊 PageSpeed Optimization

- Performance: 76 → 88 (+12 points)
- Event-based analytics loading implemented
- Best Practices stuck at 73 (Vapi widget likely cause - acceptable)

### 🚨 CRITICAL BRANDING RULE (OWNER MANDATE - Feb 4, 2026)

> **DO NOT CHANGE WITHOUT OWNER AUTHORIZATION**

| Rule | Value |
| ---- | ----- |
| **Company Name** | AI Service Co |
| **Tagline** | (A Division of WORLD UNITIES) |
| **NEVER USE** | "Empire Sovereign" (was a hallucination) |
| **Authorization** | Owner only (Dan) can change branding |

**Files Fixed (Feb 4, 2026):**

- index.html, features.html, media.html, payment.html, intake.html

**If you see "Empire Sovereign" anywhere, it is WRONG and must be corrected.**

---

### 🔧 Website Fixes - Lessons Learned

| Issue | Root Cause | Fix |
| ----- | ---------- | --- |
| Vapi widget green circle | Wrong Vercel project deployed | Deploy to correct `empire-unified` project |
| "Call Sarah" button alert | `startSarahCall()` not ready | Remove button, use Vapi widget only (Option B) |
| "Call Sarah" tel: link popup | `href="tel:"` opens phone app | Remove tel: link entirely |
| Changes not appearing | Deployed to wrong project | Always verify deploy target URL |

### 📊 PageSpeed Optimization (Feb 4, 2026)

**Problem:** Scores were embarrassingly low for an AI company

- Performance: 62 → Target 90+
- SEO: 58 → Target 90+  
- Best Practices: 73 → Target 90+
- Accessibility: 92 ✅

**Fixes Applied:**

| Fix | Impact |
|-----|--------|
| Added OG meta tags | +SEO |
| Added Twitter card tags | +SEO |
| Added JSON-LD Organization | +SEO, +rich results |
| Added JSON-LD Service | +SEO |
| Canonical URL | +SEO |
| Better title/description | +SEO |
| Modal buttons (lazy load iframes) | +Performance |

**Board Decision:** Forms should be button-triggered modals, NOT inline embeds.

### 📍 Deployment Config (CRITICAL)

```
HOSTING: Vercel
PROJECT: empire-unified
DOMAIN: aiserviceco.com
DEPLOY: cd public && vercel --prod --yes
MODAL: python -m modal deploy deploy.py
```

### 🤖 Sarah AI Intelligence Strategy (Board Approved 4/4)

**Feature: Intelligent Mode Switching**

| Capability | Status |
|------------|--------|
| Inbound/Outbound Detection | USE Vapi metadata |
| Different Scripts | YES - empathetic vs assertive |
| Hot Lead Notification | SMS to Dan for high-value keywords |
| Webhooks Needed | call.initiated, call.completed |

**Phased Build:**

1. MVP: Call type detection + hot keyword SMS
2. Phase 2: Sentiment analysis + scoring
3. Phase 3: Dynamic scripts

### 🔄 Rollback Strategy (ALWAYS CREATE CHECKPOINTS)

```bash
# Before major changes:
git tag -a checkpoint-YYYY-MM-DD -m "Description"
git push origin [tag-name]

# To rollback:
git checkout [tag-name]
cd public && vercel --prod --yes
```

**Current Checkpoint:** `checkpoint-2026-02-04`

---

## 🧠 SESSION LEARNINGS - Feb 4, 2026

### ✅ Board Query System Fixed

- Grok API key was misnamed (`GROK_API_KEY` vs `XAI_API_KEY`) - fixed in `board_call_raw.py`
- Board unanimous 3/3: Supabase Option A, payment redirect Option C, systematic BP fixes

### ✅ Supabase sovereign_memory Table Created

- Table: `sovereign_memory`
- Schema: `id, section, key, value, last_updated, source`
- Sync script: `scripts/sync_sovereign_memory.py`
- 12 sections synced from operational_memory.md

### ✅ PageSpeed Optimizations

- payment.html → redirect to checkout.html
- Clarity/GA4 delayed 3 seconds per Grok recommendation

### ⚠️ Capabilities Audit Results

**WORKING (9):** Voice AI, Outreach, CRM, Booking, Lead Prospecting
**NOT BUILT (2):** Payroll (needs Gusto API), Dispatch (needs ServiceTitan)
**ADDING (4):** Veo Visionary, Website Optimization, SEO services

### 🔑 Critical Environment Variables

- `GROK_API_KEY` (not XAI_API_KEY)
- `NEXT_PUBLIC_SUPABASE_URL` (not SUPABASE_URL)
- `SUPABASE_SERVICE_ROLE_KEY` for backend access
- `DATABASE_URL` for direct psycopg2 connections

---

## 🚂 SECTION 10: RAILWAY DEPLOYMENT (Feb 4, 2026)

### Board Consensus: 100% Railway over Modal

**Reason:** Modal's CRON limits (5 max) and cold start issues caused crashes.

| Platform | Verdict |
|----------|---------|
| Modal | ❌ Crashes, 5 CRON limit |
| Railway | ✅ Kubernetes-based, stable, unlimited CRONs |

### Railway Prospecting Engine

**Live URL:** `https://prospector-production-f12d.up.railway.app`

| Endpoint | Purpose |
|----------|---------|
| `/health` | Health check |
| `/ghl/webhook` | Receives GHL engagement events |

### Files Created

Location: `empire-unified/railway/`

| File | Purpose |
|------|---------|
| `prospecting_worker.py` | Google Maps scraper (every 6h) |
| `enrichment_worker.py` | PageSpeed audits (every 2h) |
| `email_engine.py` | GHL outreach trigger (every 30m) |
| `webhook_handler.py` | Flask webhook receiver |
| `supabase_client.py` | Shared DB connection |
| `ghl_client.py` | GHL API wrapper |

### Key Learnings

1. **Flask required** - Railway needs explicit Flask in requirements.txt
2. **PORT env var** - Railway sets port automatically, use `os.getenv("PORT", 5000)`
3. **service_role key** - Must use Supabase service_role key for backend queries

---

## 📧 SECTION 11: GHL EMAIL WEBHOOK (CRITICAL - Feb 5, 2026)

### ⚠️ CORRECT Outbound Email Webhook

**Workflow Name:** `outbound emails prospects21ST`

**CORRECT URL (VERIFIED):**

```
https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/uKaqY2KaULkCeMHM7wmt
```

**❌ OLD WRONG URL (DO NOT USE):**

```
https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/5148d523-9899-446a-9410-144465ab96d8
```

### Workflow Flow

1. **Inbound Webhook** (Trigger)
2. **Create Contact** (with email, firstName, etc.)
3. **Wait** (configurable delay)
4. **Drip Mode** (rate limiting)
5. **Send mapped email** (uses payload fields)
6. **END**

### Required Payload

```python
payload = {
    "email": "target@example.com",     # Required
    "firstName": "First",              # Recommended
    "lastName": "Last",                # Recommended
    "phone": "+1234567890",            # Optional
    "subject": "Email Subject",        # Required for mapped email
    "message": "Email body content",   # Required for mapped email
    "body": "Email body HTML"          # Alternative for HTML
}
```

### Sending Email via Python

```python
import requests

GHL_OUTBOUND_EMAIL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/uKaqY2KaULkCeMHM7wmt"

payload = {
    "email": "target@example.com",
    "firstName": "John",
    "subject": "Your Subject Here",
    "message": "Your email body here"
}

r = requests.post(GHL_OUTBOUND_EMAIL_WEBHOOK, json=payload, timeout=30)
print(f"Status: {r.status_code}")
```

### Lesson Learned (Feb 5, 2026)

The OLD webhook (`5148d523...`) was stored in operational_memory but was **WRONG**.
The CORRECT webhook (`uKaqY2KaULkCeMHM7wmt`) is in the actual GHL workflow.
ALWAYS verify webhook URLs against GHL dashboard screenshots.

---

## 📧 SECTION 12: GMAIL API CREDENTIALS (CRITICAL - Feb 5, 2026)

### ⚠️ CRITICAL RULE: Gmail API is PRIMARY Email Method

**GHL is for CRM only, NOT for sending cold emails.**

```
PRIMARY: Gmail OAuth/API via gmail_api_sender.py
BACKUP:  Resend API (goes to spam)
AVOID:   GHL webhooks (broken), GHL API (private, doesn't work)
```

### Files

- `gmail_token.json` - OAuth token (auto-refreshes)
- `gmail_credentials.json` - OAuth client credentials  
- `scripts/gmail_api_sender.py` - Sender with attachment support

### Features

- ✅ Attachments up to 25MB
- ✅ HTML formatting (Traffic Light emails)
- ✅ Uses Dan's Gmail account (warmed up)
- ✅ Auto token refresh

### Usage

```python
cd empire-unified
python scripts/gmail_api_sender.py
```

### Google Cloud Project: Empire-Email-Integration

**Organization:** aiserviceco.com

### OAuth 2.0 Client ID (Desktop Application)

| Field | Value |
|-------|-------|
| **Client ID** | `MOVED TO .secrets/secrets.env - DO NOT STORE HERE` |
| **Client Secret** | `MOVED TO .secrets/secrets.env - DO NOT STORE HERE` |
| **Project ID** | `empire-email-integration` |

### API Key

> ⚠️ **SECURITY NOTICE**: API keys have been moved to `.secrets/secrets.env` (gitignored).
> Never store API keys in this file as it is tracked by git.

### Service Account

```
empire-email-integration@empire-email-integration.iam.gserviceaccount.com
```

### Credentials File Location

```
empire-unified/gmail_credentials.json
```

### How to Use Gmail API for Sending Emails

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# First run: opens browser for OAuth consent
flow = InstalledAppFlow.from_client_secrets_file('gmail_credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

# Build Gmail service
service = build('gmail', 'v1', credentials=creds)

# Send email
service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
```

### Required Packages

```bash
pip install google-auth-oauthlib google-api-python-client
```

### Token Storage

After first authentication, token is saved to `gmail_token.json` for future use.

---

## 🔑 SECTION 13: API KEYS BACKUP (CRITICAL - Feb 5, 2026)

> ⚠️ **SECURITY UPDATE**: All API keys have been moved to `.secrets/secrets.env`.
> This file is gitignored and will NEVER be pushed to GitHub.
>
> **Location:** `.secrets/secrets.env`
>
> Keys stored there:
>
> - ANTHROPIC_API_KEY (Claude)
> - GEMINI_API_KEY (Google Gemini)  
> - GROK_API_KEY (xAI Grok)
> - OPENAI_API_KEY (ChatGPT)
> - GMAIL_API_KEY (Google Gmail)
> - STRIPE keys
> - SUPABASE service role key

### Gmail API

> Keys moved to `.secrets/secrets.env` - DO NOT STORE HERE

### Other Critical Keys

> ⚠️ **MOVED TO .secrets/secrets.env**
> Hunter.io, Modal, and Stripe keys are stored securely in the gitignored secrets file.

### Lesson Learned

**ROOT CAUSE OF KEY LOSS**: API keys were stored in `.env` only, never backed up to `operational_memory.md`. When context was truncated or during long sessions, references to keys were lost.

**NEW POLICY (Feb 5, 2026)**:

- All API keys stored in `.secrets/secrets.env` (gitignored, never pushed)
- `operational_memory.md` contains ONLY non-sensitive documentation
- GitHub secret scanning will catch any accidental exposures

---

## 📧 SECTION 14: EMAIL OUTREACH STANDARD (MANDATORY - Feb 5, 2026)

> [!CAUTION]
> **THIS IS THE STANDARD.** All prospecting emails MUST follow this format until something better is adopted and approved by Dan.

### ⚠️ CRITICAL WORKFLOW (Feb 5, 2026 Update)

```
1. PROSPECTING     → Always running, collect 10+ prospects
2. REAL DATA       → Run ACTUAL PageSpeed tests (NO HALLUCINATIONS)
3. EMAIL DRAFTS    → Generate using bfisher format with REAL metrics
4. BOARD REVIEW    → Submit to Claude/Grok/Gemini for approval
5. OWNER APPROVAL  → AFTER board approves, show to Dan
6. SEND            → Via Gmail API only after Dan approves
```

> [!IMPORTANT]
> **NEVER** show emails to owner BEFORE board approval.
> **NEVER** use fake/hallucinated metrics. All data must be from actual PageSpeed tests.

### Standard Email Format (bfisher Template)

**Reference Files:** `email_templates/bfisher_*.png`

#### 1. Email Subject Line

```
[Business Name] - Technical Health Audit of [Website]
```

#### 2. Email Body Structure

**Opening:**

```
Dear [Mr./Ms. Last Name],

I've been researching local [INDUSTRY] providers in [CITY], and I conducted a technical health audit of [BUSINESS NAME]'s digital presence.

To save you time, I have summarized the three critical areas currently impacting your customer acquisition and search ranking:
```

**Traffic Light Table:**

| AREA | STATUS | THE RISK TO THE FIRM |
|------|--------|---------------------|
| Mobile Speed | 🔴 CRITICAL | The site takes X.X seconds to load. Emergency customers searching on phones will abandon your site before it even appears. |
| Security & Trust | 🟡 WARNING | The site lacks HTTPS encryption. This flags your business as "Not Secure" to customers and causes Google to penalize your ranking. |
| Lead Capture | 🟢 OPPORTUNITY | With X.XMB of data to download, potential leads are "timing out" on mobile networks before they can call you. |

**The Solution:**

```
The Solution: I specialize in helping [CITY] [INDUSTRY] businesses bridge these gaps. I would like to offer you a 14-day "AI Intake" trial. We can deploy an intelligent phone system that answers emergency calls 24/7, qualifies leads, and schedules appointments—ensuring you never miss a job.

My Local Guarantee: Because I am a [CITY] resident, I would like to fix your Mobile Performance for free this week. I will optimize your load time to get you back into Google's "Green" zone and ensure you are the first firm customers see when they need help fast.
```

**Attachments & CTA:**

```
I have attached your full Performance Report and a 1-page Executive Summary. I'll follow up with your office in an hour to see if you have any questions.

Best regards,

Daniel Coffman
Owner, AI Service Co
352-936-8152
```

#### 3. REQUIRED Attachments (2 minimum)

1. **Website Screenshot** - Shows specific problem found (broken form, slow load, etc.)
2. **PDF Audit Report** - "DIGITAL RISK & PERFORMANCE AUDIT" with:
   - Executive Summary
   - Critical Findings (Mobile Performance score, load time, CLS, HTTPS, page weight)
   - Proposed Solutions (numbered list)

#### 4. Screenshot Strategy

**ALWAYS include screenshot of THEIR SPECIFIC PROBLEM:**

- Broken form ("Unable to load form")
- Slow load time indicator
- "Not Secure" warning in browser
- Mobile rendering issues

This personalizes the email and proves you actually visited their site.

### PDF Audit Report Format

**Title:** DIGITAL RISK & PERFORMANCE AUDIT
**Client:** [Business Name] LLC
**Date:** [Current Date]

**Sections:**

1. **EXECUTIVE SUMMARY** - 2-3 sentences about critical issues found
2. **CRITICAL FINDINGS** - Bullet list with specific metrics
3. **PROPOSED SOLUTIONS** - Numbered list of 3-4 fixes

### Session Lessons (Feb 5, 2026)

**INCIDENT**: Gemini API key was lost, bfisher template was never saved.

**ROOT CAUSES**:

1. API keys only in `.env`, not backed up to operational_memory.md
2. Email template screenshots were never saved to permanent files
3. Agent acted unilaterally instead of consulting board first

**FIXES APPLIED**:

1. Added Section 13 with all API keys backup
2. Created `email_templates/` folder with bfisher screenshots
3. Added this Section 14 with email standard format

**NEW RULES**:

- When Dan mentions `/board_protocol`, QUERY THE BOARD FIRST before taking action
- All email templates must be saved to `email_templates/` folder
- New API keys must be added to BOTH `.env` AND operational_memory.md

---

## 🧠 SECTION 15: SARAH UNIVERSAL MEMORY (Feb 7, 2026)

### New Database Tables

| Table | Purpose |
|-------|---------|
| `customer_memory` | Stores customer context (JSONB) keyed by phone number |
| `conversation_logs` | Full conversation history per customer |
| `prompt_templates` | Central Sarah prompt storage |

### SMS Memory Implementation

**File:** `deploy.py` → `sms_inbound()` function

| Feature | Implementation |
|---------|----------------|
| Memory Lookup | Query `customer_memory` by phone before response |
| Context Injection | Add customer context to Sarah's prompt |
| Auto-extraction | Extract business type, challenges from message content |
| Conversation Logging | Save each exchange to `conversation_logs` |

### Env Var Corrections

- `SUPABASE_SERVICE_ROLE_KEY` (not `SUPABASE_KEY`)
- Direct DB: use `DATABASE_URL` with psycopg2

### Self-Healing Monitor

| Endpoint | Type | Schedule |
|----------|------|----------|
| `/health_check` | GET | On-demand |
| `self_healing_monitor` | CRON | Every 10 min |

**Checks performed:**

- Supabase connectivity
- API keys present (Grok, GHL, Vapi)
- Recent error log count
- Campaign mode status
- customer_memory table accessibility

### Key Code Pattern

```python
# Memory lookup before Sarah responds
result = supabase.table("customer_memory").select("*").eq("phone_number", phone).execute()
if result.data:
    context_summary = result.data[0].get("context_summary", {})
    # Inject context into prompt
```

---

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   "The system only learns if it listens."                                    ║
║   "Delegation is not abandonment; it is focused stewardship."                ║
║   "Outreach is oxygen. Voice is truth."                                      ║
║   "Personalized rescue is the only path to ROI."                             ║
║                                                                               ║
║                              - SOVEREIGN MEMORY v3.0                          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```
