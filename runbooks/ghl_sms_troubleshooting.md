# GHL SMS Workflow Troubleshooting Runbook

## Common Error: "There is no message or attachments for this message. Skip sending."

**Root Cause:** GHL workflow tried to send SMS but `reply_text` merge field was empty or not correctly referenced.

### Causes & Fixes

| Cause | Fix |
|-------|-----|
| "Save response" not enabled | Enable checkbox on webhook step |
| Wrong merge field syntax | Use picker, not manual typing |
| Webhook returned error | Check Modal /api/sms/health |
| Response field name changed | Try all 3 fallback patterns |

---

## Workflow Configuration

### Step 1: Trigger

- **Type:** Customer Replied / Inbound Message
- **Channel:** SMS only

### Step 2: Custom Webhook (Call Modal)

- **Action:** Custom Webhook (NOT standard Webhook)
- **Method:** POST
- **URL:** `https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/reply-text`
- **Headers:** `Content-Type: application/json`
- **Body:**

```json
{
  "phone": "{{contact.phone}}",
  "message": "{{message.body}}",
  "contactId": "{{contact.id}}",
  "conversationId": "{{conversation.id}}"
}
```

- **⚠️ CRITICAL:** Enable "Save response from this webhook" checkbox ✅

### Step 3: Send SMS

- **Action:** Send SMS
- **Phone:** `{{contact.phone}}`
- **Message:** Use merge field picker → select `reply_text` from webhook response

---

## Merge Field Fallback Patterns

GHL UI varies. Try these in order:

1. **Pattern A (Step Reference):**

   ```
   {{#2.reply_text}}
   ```

   (Where #2 is the webhook step number)

2. **Pattern B (Webhook Response):**

   ```
   {{webhook.reply_text}}
   ```

3. **Pattern C (Custom Webhook):**

   ```
   {{customWebhook.reply_text}}
   ```

### How to Verify Which Works

1. Go to **Automation → Execution Logs**
2. Find a recent run
3. Expand the "Send SMS" step
4. Look at "Message Preview"
   - ✅ GOOD: Shows actual AI response text
   - ❌ BAD: Shows literal `{{reply_text}}` or is empty

---

## Step 4: Confirm Delivery (Optional)

Add webhook to confirm SMS was sent:

- **Action:** Webhook
- **Method:** POST
- **URL:** `https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/reply-sent`
- **Body:**

```json
{
  "phone": "{{contact.phone}}",
  "conversationId": "{{conversation.id}}",
  "messageId": "{{message.id}}",
  "provider": "ghl"
}
```

---

## Event Log Correlation

All events use consistent correlation_id format:

```
sms_{phone}_{timestamp}_{shortid}
```

Events emitted:

- `sms.inbound` - Inbound SMS received
- `sms.reply.generated` - AI reply generated
- `sms.reply.sent` - GHL confirmed send
- `sms.reply.failed` - Send failed
- `ghl.workflow.executed` - Workflow ran
- `ghl.workflow.error` - Workflow error

---

## Debugging Checklist

1. **Check Modal Endpoint:**

   ```powershell
   Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/health" | ConvertTo-Json
   ```

2. **Check Debug SMS:**

   ```powershell
   Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/debug/sms" | ConvertTo-Json -Depth 4
   ```

3. **Run Synthetic Test:**

   ```powershell
   Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/debug/sms?run_audit=1" | ConvertTo-Json -Depth 4
   ```

4. **Check GHL Execution Logs:**
   - Automation → Execution Logs
   - Filter by "SMS AI Auto-Reply" workflow
   - Check each step status

---

## Screenshot Guide for GHL Support

If escalating to GHL support, include:

1. Screenshot of workflow with all steps visible
2. Screenshot of webhook step configuration
3. Screenshot of "Save response" checkbox
4. Screenshot of Send SMS step with merge field
5. Execution Log showing the error
6. Copy of webhook response (from Execution Log details)
