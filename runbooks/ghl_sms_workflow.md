# GHL SMS Workflow Wiring Guide

## Overview

This document describes how to wire GHL workflows to use Modal's AI reply generation.

## Architecture

```
[Inbound SMS] → [GHL Trigger] → [Webhook to Modal] → [Modal returns reply_text] → [GHL Send SMS] → [Webhook to Modal confirm]
```

## Canonical Numbers

- **Voice (Vapi):** +1 (863) 213-2505
- **SMS (GHL):** +1 (352) 758-5336

---

## Workflow: "SMS AI Auto-Reply"

### Trigger

- **Type:** Customer Replied / Inbound Message
- **Channel:** SMS only

### Step 1: Call Modal API for Reply

- **Action:** Custom Webhook (NOT standard Webhook)
- **Method:** POST
- **URL:** `https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/reply-text`
- **Headers:**
  - `Content-Type: application/json`
- **Body (JSON):**

```json
{
  "phone": "{{contact.phone}}",
  "message": "{{message.body}}",
  "contactId": "{{contact.id}}",
  "conversationId": "{{conversation.id}}"
}
```

- **CRITICAL:** Enable "Save response from this webhook" checkbox ✅

### Step 2: Send SMS with AI Reply

- **Action:** Send SMS
- **Phone:** {{contact.phone}}
- **Message:** Use merge field picker to select `reply_text` from webhook response

**Merge Field Syntax Variants (try in order):**

1. `{{#1.reply_text}}` (step reference)
2. `{{webhook.reply_text}}`
3. `{{custom_webhook_response.reply_text}}`
4. Use the "Custom Values" picker → "Webhook Response" section

**Verification:**

- Go to Automation → Execution Logs
- Expand a recent run
- Check "Send SMS" step shows actual AI text, not literal `{{reply_text}}`

### Step 3: Confirm Delivery (Optional but Recommended)

- **Action:** Webhook
- **Method:** POST  
- **URL:** `https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/reply-sent`
- **Body:**

```json
{
  "phone": "{{contact.phone}}",
  "correlation_id": "{{#1.correlation_id}}",
  "provider": "ghl"
}
```

---

## Workflow: "Messaging Error Handler" (Optional)

### Trigger

- **Type:** Messaging Error - SMS (if available)

### Step 1: Alert Modal

- **Action:** Webhook
- **Method:** POST
- **URL:** `https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/webhook/ghl/sms/error`
- **Body:**

```json
{
  "phone": "{{contact.phone}}",
  "error": "{{error.message}}",
  "timestamp": "{{trigger.timestamp}}"
}
```

---

## Troubleshooting

### "Send SMS" sends literal `{{reply_text}}`

1. Verify "Save response" is enabled on webhook step
2. Delete the merge field and re-select from picker
3. Run "Test" on webhook step with a real contact

### No SMS received

1. Check GHL → Execution Logs for errors
2. Check Modal `/api/debug/sms` for events
3. Verify A2P registration on +1 (352) 758-5336

### Modal returns error

1. Check `/api/sms/health` endpoint
2. Check Gemini API key in Modal secrets
