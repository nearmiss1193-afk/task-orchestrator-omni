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
