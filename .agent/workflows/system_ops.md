---
description: Master protocol - forces agent to read operational_memory.md before any task
---
# System Operations Protocol

// turbo-all

## Purpose

Ensure agent reads and follows all operational rules and protocols in `operational_memory.md` before executing any task.

> [!CAUTION]
> **WHEN USER INVOKES /system_ops:**
>
> 1. STOP all current action
> 2. READ operational_memory.md FIRST
> 3. ACKNOWLEDGE key rules that apply to current task
> 4. ONLY THEN proceed with task
>
> **DO NOT skip reading operational memory. Past failures happened because rules were ignored.**

## Complete Steps (MANDATORY)

### Step 1: Read Operational Memory

```bash
# View the operational memory file
view_file c:\Users\nearm\.gemini\antigravity\scratch\empire-unified\operational_memory.md
```

Key sections to review:

- CRITICAL: READ FIRST (lines 1-70)
- EMAIL VERIFICATION (if sending emails)
- GHL API LIMITATION (if using GHL)
- BOARD LOCK rules (if making major decisions)

### Step 2: Acknowledge Applicable Rules

Before proceeding, explicitly state:

- [ ] Which rules from operational_memory apply to this task
- [ ] How you will follow each applicable rule
- [ ] What verification steps you will take

### Step 3: Check for Relevant Workflows

If the task involves:

- **Email outreach** → Use `/email_outreach`
- **Board decisions** → Use `/board_protocol`
- **Site deployment** → Use `/save_protocol`
- **Research needed** → Use `/research_protocol`

### Step 4: Execute with Verification

Follow the task while:

- Checking operational_memory rules at each step
- NOT guessing or assuming (verify everything)
- Documenting what you did

### Step 5: Report Results

After task completion:

- State what was done
- State what was verified
- State any issues found

## Key Operational Rules (Quick Reference)

| Rule | Summary |
|------|---------|
| **NEVER guess emails** | Use /email_outreach, research before sending |
| **GHL API doesn't work** | Use webhooks instead |
| **Deploy to Vercel** | NOT Netlify, verify aiserviceco.com |
| **Board for major decisions** | 3/4 vote required |
| **Push before deploy** | Git push is mandatory |
| **Verify database results** | Exit code 0 ≠ success |

## Incident Log (Why This Protocol Exists)

| Date | Incident | Root Cause |
|------|----------|------------|
| Feb 5, 2026 | 6/10 emails bounced | Guessed email addresses |
| Jan 25, 2026 | Deploy "succeeded" but didn't work | Didn't verify database |
| Jan 25, 2026 | Wrong Supabase key | Used anon instead of service_role |

## Files to Reference

- `operational_memory.md` - Master rules document
- `.secrets/secrets.env` - API keys and credentials
- `board_call_raw.py` - Board protocol script
- `scripts/` - Execution scripts

## NEVER DO

❌ Skip reading operational_memory.md
❌ Assume you remember the rules
❌ Proceed without acknowledging applicable rules
❌ Guess instead of verifying
❌ Report success without verification

## ALWAYS DO

✅ Read operational_memory.md at start of task
✅ State which rules apply
✅ Use appropriate sub-workflows (/email_outreach, /board_protocol)
✅ Verify results match expectations
✅ Report with actual data, not assumptions
