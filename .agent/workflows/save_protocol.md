---
description: Standard operating procedure for session end - ALWAYS run this
---

# Save Protocol SOP

> [!CAUTION]
> **THIS IS MANDATORY.** Before EVERY `notify_user` call that updates the user on completed work, you MUST include ALL items from the checklist below. NO EXCEPTIONS.

## ⛔ HARD RULE: Minimum notify_user Content

Every status update to the user MUST contain:

- [ ] **Dashboard Link**: <https://www.aiserviceco.com/dashboard.html>
- [ ] **What Was Done**: Bullet list of completed actions
- [ ] **System States**: Campaign/Sarah/Cloud status
- [ ] **Recovery Command**: Exact `python ...` command to restart
- [ ] **Next Priority**: 1-2 recommendations

If any of these are missing, THE PROTOCOL IS VIOLATED.

---

## ⚠️ MANDATORY: Research Protocol

**BEFORE using ANY new platform, API, or tool, RUN `/research_protocol`**

See: `.agent/workflows/research_protocol.md` for full process.

Quick checklist:

1. Search web for official docs
2. Find second source (tutorial/SO)
3. Cross-reference both sources
4. Document in `operational_memory.md`
5. THEN implement

This applies to: Railway, Modal, Vercel, new APIs, new libraries, etc.

---

## Required Actions at Session End

### 1. Git Commit & Push

// turbo

```bash
git add -A && git commit -m "💾 SAVE PROTOCOL: [brief description]"
git push origin main
```

### 1.5 SEND EMAIL SUMMARY (MANDATORY)

// turbo

```bash
python send_session_summary.py
```

This sends the session summary to <nearmiss1193@gmail.com> via GHL webhook.

### 2. Status Report (Always Include)

**Dashboard:** <https://www.aiserviceco.com/dashboard.html>

**Owner Contacts:**

- <owner@aiserviceco.com>
- <nearmiss1193@gmail.com>

### 3. Session Summary Template

```
📊 SESSION SUMMARY - [DATE]

**Completed:**
- [List items]

**Active Systems:**
- Campaign Status: [Running/Idle]
- Sarah AI: [Active/Standby]
- Modal Cloud: [✅/❌]
- GHL Integration: [✅/❌]
- Supabase: [✅/❌]

**Git Commits:**
- [commit hash] - [message]
```

### 4. Recovery Instructions (REQUIRED)

Send user exact commands to restart system:

```bash
# Start watchdog (auto-restarts swarm):
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified
python watchdog.py

# Or start swarm directly:
python continuous_swarm.py

# Start portal:
cd apps\portal && npm start

# Check Modal cloud:
python -m modal app list
```

### 5. Current Capabilities Summary (REQUIRED)

Include what the system CAN do:

- Prospecting (Apollo API)
- Email outreach (GHL webhooks)
- SMS outreach (GHL webhooks)
- AI Calls (Vapi - Rachel/Sarah)
- Lead tracking (Supabase)
- Cloud webhooks (Modal)

### 6. Recommendations (REQUIRED)

Include 2-3 next priority actions.

### 7. Update Brain

- Update `knowledge_base/operational_memory.md` with learnings
- Log any new credentials or configurations

### 8. Browser Cleanup

- Close duplicate tabs
- Keep max 5 tabs open

## Quick Links

| Resource | URL |
|----------|-----|
| Dashboard | <https://www.aiserviceco.com/dashboard.html> |
| GHL | <https://app.gohighlevel.com> |
| Vapi | <https://dashboard.vapi.ai> |
| Supabase | <https://supabase.com/dashboard> |
| Modal | <https://modal.com/apps> |

## Cloud Endpoints

| Endpoint | URL |
|----------|-----|
| Health | nearmiss1193-afk--empire-webhooks-health.modal.run |
| Outreach Trigger | nearmiss1193-afk--empire-webhooks-trigger-outreach.modal.run |
| Inbound Lead | nearmiss1193-afk--empire-webhooks-inbound-lead.modal.run |
