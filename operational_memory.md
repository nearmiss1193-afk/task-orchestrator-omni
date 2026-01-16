# Empire Unified - Operational Memory

> **Last Updated:** Jan 15, 2026
> **Purpose:** Consolidated monthly learnings, configurations, and SOPs for system recovery

---

## January 2026 Session Learnings

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
| ------- | ------- | -------- |
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
