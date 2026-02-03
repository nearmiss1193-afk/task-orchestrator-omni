# Empire Unified - Operational Memory

## Jan 30: Sovereign 2.0 Hardening

- **Architecture Split**:
  - `nexus-engine`: Dedicated to crons and outreach workers. Stable, high-priority.
  - `nexus-portal`: Dedicated to webhooks, landing pages, and the secured dashboard.
- **Security Lockdown**:
  - Dashboard moved to `sov_8k2_cmd.html`.
  - `robots.txt` disallows dashboard indexing.
  - Local Key: `empire_2026` required for dashboard persistence.
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
