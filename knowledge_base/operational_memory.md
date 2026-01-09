# Empire Operational Memory

> **Purpose:** Persistent memory file for cross-session knowledge retention.
> **Last Updated:** 2026-01-08T20:41 EST

---

## 🕐 Business Rules

### Calling Rules

- **7 AM Start:** NO outbound calls before 7 AM local time
- **7 PM Cutoff:** Stop calling after 7 PM local time for each timezone
- **Follow-the-Sun Pattern:** When EST hits 7 PM, shift to Central → Mountain → Pacific
- **Window:** 7 AM - 7 PM local time for all outbound calls
- **Call Pacing:** 1 call every 10 minutes between leads

### Email Best Practices

- **Optimal Send Times:** 9-11 AM, 1-3 PM local time
- **Avoid:** Before 8 AM, after 6 PM, weekends for business emails

### SMS Rules

- **Same 8 AM - 7 PM window as calls**
- **Follow timezone rules before sending**

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
