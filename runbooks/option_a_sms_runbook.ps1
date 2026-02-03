# ============================================================
# OPTION A SMS RUNBOOK - Reply-Text Only Architecture
# Generated: 2026-01-18
# ============================================================
# 
# Architecture:
# 1. GHL receives inbound SMS
# 2. GHL calls our endpoint to GET reply text
# 3. GHL sends the reply SMS natively (no API key needed)
# 4. GHL calls us back to confirm sent
#
# Numbers:
# - Voice (Call Sarah): +1 (863) 213-2505 [Vapi]
# - Text (SMS Sarah): +1 (352) 758-5336 [GHL]

# ============================================================
# P1: GHL WORKFLOW SETUP INSTRUCTIONS
# ============================================================
<#
STEP 1: Create New Workflow
1. Go to GHL > Automation > Workflows > + Create Workflow
2. Name: "SMS Auto-Reply via AI"
3. Choose "Start from Scratch"

STEP 2: Add Trigger
1. Click "+ Add Trigger"
2. Select "Customer Replied" or "Inbound Message" or "SMS Received"
3. Filters:
   - Message Type = SMS
   - (Optional) Exclude internal messages

STEP 3: Add Webhook Action (Get Reply Text)
1. Click "+" to add action
2. Select "Webhook" (Outbound Webhook)
3. Configure:
   - Name: "Get AI Reply"
   - Method: POST
   - URL: https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/reply-text
   - Body Type: Custom JSON
   - Body:
     {
       "phone": "{{contact.phone}}",
       "message": "{{message.body}}",
       "contactId": "{{contact.id}}",
       "conversationId": "{{conversation.id}}"
     }

   ALTERNATIVE MERGE FIELD OPTIONS (if above don't work):
   Template B:
     {
       "phone": "{{contact.phone_number}}",
       "message": "{{trigger.message.body}}",
       "contactId": "{{contact.contact_id}}",
       "conversationId": "{{trigger.conversation_id}}"
     }

   Template C (minimal):
     {
       "phone": "{{contact.phone}}",
       "message": "{{message.body}}"
     }

STEP 4: Store Reply Text in Custom Field
1. FIRST: Create a custom field (if not exists):
   - Go to Settings > Custom Fields
   - Create field: Name = "AI Last Reply Text", Field Key = "ai_last_reply_text"
   - Type = Text (Long Text / Multi-line)
2. Add Action after Webhook: "Update Contact Field"
   - Field: ai_last_reply_text
   - Value: {{webhook.reply_text}}

   NOTE: If "{{webhook.reply_text}}" is not available in picker:
   - Try "{{Get AI Reply.reply_text}}" (using webhook action name)
   - Or store the entire webhook response and extract later

STEP 5: Add Send SMS Action
1. Click "+" to add action
2. Select "Send SMS"
3. Configure:
   - Message: {{contact.ai_last_reply_text}}
   - OR directly use webhook response if supported: {{Get AI Reply.reply_text}}

STEP 6: Add Confirmation Webhook (Reply Sent Callback)
1. Click "+" to add action
2. Select "Webhook" (Outbound Webhook)
3. Configure:
   - Name: "Confirm Sent"
   - Method: POST
   - URL: https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/reply-sent
   - Body:
     {
       "phone": "{{contact.phone}}",
       "conversationId": "{{conversation.id}}",
       "correlation_id": "{{Get AI Reply.correlation_id}}",
       "provider": "ghl"
     }

STEP 7: Save and Publish
1. Click "Save"
2. Toggle workflow to "Published"

#>

# ============================================================
# P5: VERIFICATION COMMANDS
# ============================================================

Write-Host "`n=== 1. Test Reply-Text Endpoint ===" -ForegroundColor Cyan
$body = @{
    phone          = "+13529368152"
    message        = "My AC is broken and its really hot!"
    contactId      = "test_verification"
    conversationId = "conv_test_001"
} | ConvertTo-Json
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/reply-text" -Method POST -Body $body -ContentType "application/json"

# Expected output:
# reply_text: <AI generated response ending in -Sarah>
# correlation_id: sms_13529368152_20260118..._xxxx

Write-Host "`n=== 2. Test Reply-Sent Callback ===" -ForegroundColor Cyan
$body = @{
    phone          = "+13529368152"
    conversationId = "conv_test_001"
    correlation_id = "sms_test_001"
    provider       = "ghl"
} | ConvertTo-Json
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/reply-sent" -Method POST -Body $body -ContentType "application/json"

# Expected output:
# status: ok
# logged: True

Write-Host "`n=== 3. Check SMS Health ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/health" | ConvertTo-Json

# What "GREEN" looks like:
# {
#   "status": "ok",
#   "sms_pipeline_healthy": true,
#   "last_sms_inbound_ts": "2026-01-18T...",
#   "last_sms_reply_generated_ts": "2026-01-18T...",
#   "last_sms_reply_sent_ts": "2026-01-18T...",
#   "unreplied_count_60s": 0,
#   "last_error": null
# }

Write-Host "`n=== 4. Check SMS Debug ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/debug/sms" | ConvertTo-Json -Depth 4

# ============================================================
# SUPABASE SQL VERIFICATION
# ============================================================
<#
-- Last 20 SMS events
SELECT ts, type, entity_id as phone, correlation_id, 
       payload->>'intent' as intent,
       payload->>'model' as model
FROM event_log_v2
WHERE type LIKE 'sms.%'
ORDER BY ts DESC
LIMIT 20;

-- Count unreplied in last 10 minutes
WITH inbound AS (
    SELECT entity_id, correlation_id, ts
    FROM event_log_v2
    WHERE type = 'sms.inbound'
    AND ts > NOW() - INTERVAL '10 minutes'
),
sent AS (
    SELECT entity_id, correlation_id, ts
    FROM event_log_v2
    WHERE type = 'sms.reply.sent'
    AND ts > NOW() - INTERVAL '10 minutes'
)
SELECT i.entity_id, i.correlation_id, i.ts as inbound_ts, s.ts as sent_ts,
       CASE WHEN s.ts IS NULL THEN 'MISSING' ELSE 'OK' END as status
FROM inbound i
LEFT JOIN sent s ON i.entity_id = s.entity_id
ORDER BY i.ts DESC;

-- Check for deadman incidents
SELECT ts, type, payload
FROM event_log_v2
WHERE type LIKE 'incident.%' OR type LIKE 'deadman.%'
ORDER BY ts DESC
LIMIT 10;
#>

# ============================================================
# SUCCESS CRITERIA (What "GREEN" means)
# ============================================================
<#
[ ] /api/sms/reply-text returns reply_text + correlation_id
[ ] /api/sms/reply-sent returns status: ok, logged: True
[ ] /api/sms/health shows:
    - sms_pipeline_healthy: true
    - unreplied_count_60s: 0
    - last_sms_inbound_ts populated
    - last_sms_reply_sent_ts populated (after GHL workflow runs)
[ ] Supabase shows sms.inbound + sms.reply.generated + sms.reply.sent events
[ ] Real text to +1 (352) 758-5336 receives AI reply within 60 seconds
#>

# ============================================================
# RECOVERY COMMANDS
# ============================================================
<#
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified
python -m modal deploy modal_orchestrator_v3.py
python send_session_summary.py
#>
