# Empire Operational Memory

> **Purpose:** Persistent memory file for cross-session knowledge retention.
> **Last Updated:** 2026-01-10T11:15 EST

---

## 👑 OWNER INFORMATION

| Field | Value |
|-------|-------|
| **Primary Email** | <owner@aiserviceco.com> |
| **Secondary Email** | <nearmiss1193@gmail.com> |
| **Dashboard** | <https://www.aiserviceco.com/dashboard.html> |
| **GHL Portal** | <https://app.gohighlevel.com> |
| **Vapi Dashboard** | <https://dashboard.vapi.ai> |

---

## 🚨 CRITICAL: Phone Number Architecture (2026-01-10)

### Current Phone Numbers in Vapi

| Number | Type | Status | Notes |
|--------|------|--------|-------|
| +1 (863) 213 2505 | Vapi-purchased | ⚠️ Error | "AI Service Co" - showing TypeError |
| +1 (863) 692 8548 | Vapi-purchased | ✅ Active | "John Roofing Line" |
| +1 (904) 512 9565 | Vapi-purchased | ✅ Active | "Riley (ALF Specialist)" |
| +1 (863) 337 3705 | Vapi-purchased | ✅ Active | Untitled |
| +1 (863) 337 3601 | Vapi-purchased | ✅ Active | Untitled |
| +1 (863) 692 8474 | Vapi-purchased | ✅ Active | "Sarah (Temporarily John)" |
| +1 (863) 260 8351 | **Twilio-imported** | ✅ UNLIMITED | "Empire Invoice (Twilio)" |

### Vapi Daily Limits

- **Vapi-purchased numbers have DAILY OUTBOUND CALL LIMITS**
- **Twilio-imported numbers have NO LIMITS**
- Use `VAPI_TWILIO_PHONE_ID` for high-volume campaigns

### GHL Outbound Calling (Alternative to Vapi)

- GHL can make outbound calls via Workflows
- Trigger: Inbound Webhook or "Contact Tag Added"
- Action: "Call Contact" (connects agent) or "Voicemail Drop"
- **Does NOT require Vapi** - uses GHL's own infrastructure

---

## 🕐 Business Rules

### ⏰ TIMEZONE ENFORCEMENT (MANDATORY)

**NO calls or SMS before 8 AM or after 7 PM in the lead's local timezone unless specifically requested by the lead.**

| State | Timezone | UTC Offset | Example: 8 PM ET |
|-------|----------|------------|------------------|
| FL, GA, NY | Eastern (ET) | UTC-5 | 8 PM |
| TX, IL, LA | Central (CT) | UTC-6 | 7 PM |
| AZ, CO, NM | Mountain (MT) | UTC-7 | 6 PM |
| CA, NV, WA | Pacific (PT) | UTC-8 | 5 PM |
| HI | Hawaii (HT) | UTC-10 | 3 PM |

### Calling Rules

- **8 AM Start:** NO outbound calls before 8 AM local time
- **7 PM Cutoff:** Stop calling after 7 PM local time
- **Window:** 8 AM - 7 PM local time for all outbound calls
- **One Touch Per Day:** No multiple calls in one day unless lead asks
- **Follow-the-Sun:** When EST hits 7 PM, shift to Central → Mountain → Pacific → Hawaii

### SMS Rules

- **Same 8 AM - 7 PM window as calls**
- **One SMS per day max** unless lead requests more
- **Always check timezone before sending**

### Email Best Practices

- **Optimal Send Times:** 9-11 AM, 1-3 PM local time
- **Avoid:** Before 8 AM, after 6 PM, weekends for business emails

---

## 🎯 Campaign State

### Active Leads by Timezone (as of 2026-01-08)

- **Florida (EST):** 84 leads - paused after 7 PM EST
- **Texas (CT):** 5 leads
- **Arizona (MT):** 8 leads
- **California (PT):** 10 leads

### Sarah AI Status

- 6 call transcripts recorded today
- Drip campaign running autonomously
- 10-minute interval between calls

---

## 🔑 Critical Credentials

| Service | Env Variable | Status |
| --- | --- | --- |
| Supabase | `NEXT_PUBLIC_SUPABASE_URL` | ✅ |
| Vapi | `VAPI_PRIVATE_KEY` | ✅ |
| GHL | `GHL_AGENCY_API_TOKEN` | ✅ (updated 2026-01-08) |
| Resend | `RESEND_API_KEY` | ✅ |
| Gmail | `gmail_token.json` | ✅ |

---

## 📋 User Preferences

### Communication Style

- Direct, concise responses
- Status reports in table format when possible
- Autonomous execution preferred

### Approval Workflows

- Auto-proceed on routine tasks
- Notify on major architectural changes
- Request approval for external API costs

### Recovery Protocols

- Run `python send_save_protocol.py` at session end
- Backup via `python backup_protocol_v2.py`
- System health: `python cloud_inspector.py`

### Morning SOP (Daily Check)

1. **Check Campaign Status:**

   ```bash
   python get_transcripts.py  # View overnight call results
   ```

2. **Check Lead Pipeline:**

   ```bash
   python get_campaign_status.py  # Lead counts by status
   ```

3. **Review Terminal for Errors:**
   - Check `launch_drip_campaign.py` terminal for issues
   - Look for API errors, rate limits, or failed calls
4. **Verify Sarah is Active:**
   - Confirm drip campaign is running (7 AM window now open)
   - FL leads callable after 7 AM EST

---

## 🧠 Learnings Log

### 2026-01-10

- **Vapi Hit Daily Limit:** Vapi-purchased numbers have daily outbound call caps
- **Solution:** Import Twilio number OR use GHL workflows for outbound
- **GHL Integration Working:** webhook successfully accepting leads (HTTP 200)
- **Supabase Schema Mismatch:** Live table uses `company_name`, NOT `first_name`/`last_name`
- **Fix:** Use minimal insert with `status` + `last_called` columns (HTTP 201)
- **campaign_v2.py Created:** Clean production script with correct API formats
- **Git Saved:** Commit `d025228` - all changes preserved

### 2026-01-08

- 83 leads had `failed_init` due to phone in `agent_research` JSON not top-level
- Fix: Reset status to `ready_to_send`, campaign handles extraction
- GHL token was expired - user refreshed via Private Integrations page
- Dashboard data exists in Supabase, frontend filtering issue suspected
- Resend free tier cannot email unverified domains (`aiserviceco.com`)

---

## 🚨 Pending User Actions

- [ ] Google Ads verification (Customer ID: 810-390-2080)
- [ ] Google Business Profile verification
- [ ] Consider Hunter.io/Apollo.io for lead enrichment tomorrow

---

## 📚 Research Learnings (2026-01-08)

### Voice AI (Vapi) Optimization

- Target latency: <500ms end-to-end
- Use Groq LLM + ElevenLabs Flash v2.5 for speed
- Shorten system prompts, use streaming

### Lead Enrichment

- Hunter.io: Combined API (email + company) - 100+ data points
- Apollo.io: 275M contacts, real-time enrichment
- Clay: Waterfall enrichment across 150+ providers

### Multi-Agent Frameworks

- LangGraph: Best for complex stateful workflows
- CrewAI: Best for role-based agent teams (production-ready)
- AutoGen: Best for conversational prototyping

### Self-Improving Systems

- Feedback loops are critical for continuous refinement
- Human-in-the-loop prevents model collapse
- Automated prompt refinement based on outcomes

**Full research:** `knowledge_base/ai_research_2025.md`

---

## 🛠️ Engineering Standards (SOP)

### Crash Resilience & Auto-Recovery Protocol

**Mandatory for all automation scripts (Orchestrators/Managers).**

1. **Subprocess Isolation:**
    - Do NOT run critical worker logic in the main thread.
    - Use `subprocess.run(capture_output=True)` to isolate individual tasks.

2. **Crash Detection:**
    - Check `res.returncode != 0`.
    - Capture `res.stderr` (last 200 chars) for immediate context.

3. **Auto-Quarantine (No Stalls):**
    - If a worker crashes, **IMMEDIATELY** update the lead's status to `system_crash`.
    - Log the error in the `leads` table `notes` column.
    - *Result:* The pipeline must continue processing the next lead immediately. The campaign must never stall due to a single bad record or bug.

4. **Self-Correction (Future):**
    - Scripts should attempt one retry or flag for "Medic Agent" intervention.

## 1.4 Pricing Architecture (Golden Standard)

- **Unified Pricing Model**: $297/mo (Starter/Growth)
- **Authority**: This document is the SINGLE SOURCE OF TRUTH for pricing.
- **Validation**: All HTML pages must match this price.
- **Tiers**:
  - Starter: $297/mo
  - Growth: $497/mo (Only if explicitly upsold, default is $297)
  - Scale: $997/mo

### 1.5 Protocol: Deployment & Verification

- **Pre-Deployment**: Run `python verify_site_integrity.py`.
- **Post-Deployment**: Check `vercel-deploy.log`.
- **Git State**: Always `git status` before `git commit` to ensure `public/` assets are staged.

---
