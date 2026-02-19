# Notification System Fix — Feb 18, 2026

## Problem

Dan stopped receiving call/chat alerts. Christina from "Call Me Now" called Sarah twice and Dan was never notified.

## Root Causes (3 layers)

### 1. Import Error Kills Webhook (PRIMARY)

- `deploy.py` line 657: `from modules.voice.sales_persona import ...` FAILS
- `modules/voice` is NOT in the Modal image mount list (`core/image_config.py` lines 42-51)
- Line 663: `return {"status": "import_error"}` — exits the ENTIRE webhook handler
- `end-of-call-report` handler at line 852 NEVER executes
- **Fix**: Don't `return` on import error for `end-of-call-report` events

### 2. Wrong Email Address

- Code sent to `dan@aiserviceco.com` — doesn't exist
- Dan's actual email: `owner@aiserviceco.com`

### 3. GHL Balance Low

- GHL webhook returned 422 for Dan's phone number
- Two possible causes: low balance OR Dan not a GHL contact
- When balance reloaded → 200 Success

## Current Notification Flow (deploy.py end-of-call-report)

1. **Resend Email** → `owner@aiserviceco.com` (primary, most reliable)
2. **Supabase Log** → `system_health_log` table with `check_name = "call_alert"`
3. **GHL Webhook** → SMS to `+13529368152` (fallback, requires GHL balance)

## Key Files

- `deploy.py` lines 876-940: Triple-fallback notification code
- `core/image_config.py` line 60-72: Modal VAULT secrets (has RESEND_API_KEY)
- `core/image_config.py` lines 42-51: Modal image mounts (missing `modules/voice`)

## Pricing (Current as of Feb 18)

- Free 2-week trial
- $99/month normal
- **50% off = $49/month** (3-day limited offer)
- **Grandfathered rate**: $49/mo forever if they stay, $99 if they cancel and rejoin

## Vapi Server URLs

All assistants point to: `https://nearmiss1193-afk--ghl-omni-automation-vapi-webhook.modal.run`

- Sarah: `ae717f29-6542-422f-906f-ee7ba6fa0bfe`
- Sarah Spartan: `1a797f12-e2dd-4f7f-b2c5-08c38c74859a`
- Rachel: `033ec1d3-e17d-4611-a497-b47cab1fdb4e`
