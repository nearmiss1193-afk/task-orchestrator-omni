# SMS Reply Assurance Runbook

> **Mission:** Every inbound SMS MUST result in an actual reply to the customer.

---

## GHL Workflow Validation Checklist

### ✅ Pre-Flight Checklist

| Step | Check | Pass Criteria |
|------|-------|---------------|
| 1 | Trigger is "Customer Replied" or "Inbound Message" | SMS channel only |
| 2 | Webhook step has "Save response" enabled | Checkbox ✅ |
| 3 | Webhook URL is correct | `https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/reply-text` |
| 4 | Send SMS uses correct merge field | `{{#2.reply_text}}` (or step number) |
| 5 | Execution Logs show populated message | Not blank/empty |

---

## Merge Field Patterns (Try in Order)

GHL UI varies. If one fails, try the next:

1. **Step Reference:** `{{#2.reply_text}}` (where 2 = webhook step number)
2. **Webhook Response:** `{{webhook.reply_text}}`
3. **Custom Webhook:** `{{customWebhook.reply_text}}`

### How to Verify

1. Go to **Automation → Execution Logs**
2. Find a recent "SMS AI Auto-Reply" workflow run
3. Expand the "Send SMS" step
4. Look at **Message Preview**:
   - ✅ GOOD: Shows actual AI text
   - ❌ BAD: Shows `{{reply_text}}` literal or is empty

---

## 60-Second Triage Script

**When customer says "I never got a reply":**

```
STEP 1 (10s): Check API health
→ curl https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/health

STEP 2 (20s): Check GHL Execution Logs
→ Look for customer's phone number
→ Check if workflow ran AND Send SMS succeeded

STEP 3 (15s): If "Skip sending" error
→ Fix: Change merge field to {{#2.reply_text}}
→ Republish workflow

STEP 4 (15s): If no workflow ran
→ Check trigger configuration
→ Verify contact has SMS consent
```

---

## Common Errors + Fixes

### Error: "There is no message or attachments for this message. Skip sending."

**Cause:** Merge field returned empty

**Fix:**

1. Open GHL workflow
2. Find webhook step (usually step 2)
3. Ensure "Save response from this webhook" is ✅ enabled
4. Change Send SMS message to: `{{#2.reply_text}}`
5. Republish workflow
6. Test by texting the number

### Error: Webhook timeout

**Cause:** Modal cold start too slow

**Fix:**

1. Check Modal deployment: `python -m modal app list`
2. Redeploy if needed: `python -m modal deploy modal_orchestrator_v3.py`
3. Modal has 60s timeout by default

### Error: No workflow execution at all

**Cause:** Trigger misconfigured or contact missing

**Fix:**

1. Verify trigger is "Customer Replied" for SMS channel
2. Check contact exists in GHL
3. Check contact has SMS consent enabled

---

## Self-Heal Playbook

### Detection Rules

| Event | Detection | Response |
|-------|-----------|----------|
| `sms.inbound` without `sms.reply.sent` in 60s | Deadman monitor | Alert + regenerate |
| `sms.synthetic.fail` | Synthetic monitor | Alert + investigate |
| GHL "Skip sending" error | Execution log pattern | Suggest merge field fix |

### Automatic Remediation Suggestions

When detecting "Skip sending" error in logs:

```
⚠️ REMEDIATION REQUIRED

Problem: GHL Send SMS failed - "There is no message... Skip sending"

Fix:
1. Open workflow: Automation → SMS AI Auto-Reply
2. Edit Send SMS step
3. Change message body to: {{#2.reply_text}}
   (Replace 2 with your actual webhook step number)
4. Republish workflow
5. Test with a real SMS

Root cause: Merge field not referencing saved webhook response
```

---

## Monitoring Commands

### Check SMS Health (PowerShell)

```powershell
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/health" | ConvertTo-Json
```

### Run Synthetic Audit

```powershell
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/debug/sms?run_audit=1" | ConvertTo-Json -Depth 4
```

### Check Unreplied in Supabase

```sql
SELECT type, ts, entity_id, correlation_id
FROM event_log_v2
WHERE type = 'sms.inbound'
  AND ts > NOW() - INTERVAL '1 hour'
  AND correlation_id NOT IN (
    SELECT correlation_id FROM event_log_v2 
    WHERE type = 'sms.reply.sent' AND ts > NOW() - INTERVAL '1 hour'
  )
ORDER BY ts DESC;
```

---

## Escalation Path

1. **First:** Check GHL Execution Logs
2. **Second:** Check `/api/sms/health` endpoint
3. **Third:** Check Modal deployment status
4. **Fourth:** Contact owner at <nearmiss1193@gmail.com>

---

## Canonical Numbers

| Label | Number | Provider |
|-------|--------|----------|
| **VOICE** | (863) 213-2505 | Vapi |
| **TEXT** | (352) 758-5336 | GHL |
