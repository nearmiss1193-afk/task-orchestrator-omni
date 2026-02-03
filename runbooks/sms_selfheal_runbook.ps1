# SMS Self-Healing Runbook
# Generated: 2026-01-18
# For: Empire Unified - Modal v3 API

# ============================================================
# P1: GHL WORKFLOW SETUP (MOST LIKELY MISSING PIECE)
# ============================================================
#
# 1. Go to GHL > Automation > Workflows > Create Workflow
# 2. Add Trigger: "Inbound Message" or "SMS Received" or "Message Received"
# 3. Add Action: "Webhook"
# 4. Configure Webhook:
#    - Method: POST
#    - URL: https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/webhook/ghl/sms/inbound
#    - Body Type: Custom JSON
#    - Body:
#      {
#        "phone": "{{contact.phone}}",
#        "message": "{{message.body}}",
#        "contactId": "{{contact.id}}",
#        "conversationId": "{{conversation.id}}"
#      }
# 5. Save and Publish workflow
# 6. Test by texting +1 (352) 758-5336

# ============================================================
# TEST ENDPOINTS
# ============================================================

# 1. Health check
Write-Host "=== Health Check ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health" | ConvertTo-Json

# 2. SMS Debug endpoint
Write-Host "`n=== SMS Debug ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/debug/sms" | ConvertTo-Json -Depth 5

# 3. SMS Health
Write-Host "`n=== SMS Health ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/health" | ConvertTo-Json

# 4. Routing Truth
Write-Host "`n=== Routing Truth ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/routing/truth" | ConvertTo-Json

# 5. Simulate inbound SMS (for testing)
Write-Host "`n=== Simulate Inbound SMS ===" -ForegroundColor Cyan
$body = @{
    phone          = "+13529368152"
    message        = "Hi, I need help with my AC"
    contactId      = "test_contact_123"
    conversationId = "test_conv_456"
} | ConvertTo-Json
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/webhook/ghl/sms/inbound" -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json

# ============================================================
# SUPABASE VERIFICATION QUERIES
# ============================================================
# Run these in Supabase SQL Editor:

<#
-- Last 10 SMS inbound events
SELECT ts, type, entity_id as phone, correlation_id, payload->>'body' as message
FROM event_log_v2
WHERE type = 'sms.inbound'
ORDER BY ts DESC
LIMIT 10;

-- Last 10 SMS reply events
SELECT ts, type, entity_id as phone, payload->>'method' as method, payload->>'to' as to_phone
FROM event_log_v2
WHERE type LIKE 'sms.reply.%'
ORDER BY ts DESC
LIMIT 10;

-- Last 10 GHL errors
SELECT ts, payload->>'error' as error
FROM event_log_v2
WHERE type = 'error.occurred' AND source = 'ghl'
ORDER BY ts DESC
LIMIT 10;

-- Deadman heartbeats (should see every 2 min)
SELECT ts, type, payload
FROM event_log_v2
WHERE type IN ('deadman.heartbeat', 'incident.deadman')
ORDER BY ts DESC
LIMIT 10;

-- Check for stalled messages (inbound without reply)
WITH inbound AS (
    SELECT entity_id as phone, MAX(ts) as last_inbound
    FROM event_log_v2
    WHERE type = 'sms.inbound'
    GROUP BY entity_id
),
replied AS (
    SELECT entity_id as phone, MAX(ts) as last_reply
    FROM event_log_v2
    WHERE type = 'sms.reply.sent'
    GROUP BY entity_id
)
SELECT i.phone, i.last_inbound, r.last_reply,
    EXTRACT(EPOCH FROM (i.last_inbound - COALESCE(r.last_reply, '1970-01-01'::timestamptz))) as seconds_since_reply
FROM inbound i
LEFT JOIN replied r ON i.phone = r.phone
WHERE i.last_inbound > COALESCE(r.last_reply, '1970-01-01'::timestamptz)
ORDER BY i.last_inbound DESC;
#>

# ============================================================
# IF BROKEN, DO THIS
# ============================================================

<#
1. Check /api/debug/sms - are there any sms.inbound events?
   - If NO: GHL workflow is not configured. Follow P1 setup above.
   - If YES but no sms.reply.sent: Check ghl_errors in the debug output

2. Check /api/routing/truth - is sms_reply_stale = true?
   - If YES: Pipeline is stalled. Check error logs.

3. GHL API Key issues:
   - Go to GHL > Settings > API > Get new key
   - Run: modal secret create empire-secrets GHL_API_KEY="<new_key>" --force
   - Redeploy: python -m modal deploy modal_orchestrator_v3.py

4. Force redeploy:
   cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified
   python -m modal deploy modal_orchestrator_v3.py

5. Check Modal logs:
   python -m modal app logs empire-api-v3

6. Manual SMS reply test (via GHL webhook):
   $body = @{phone="+13529368152";message="Test from Modal"} | ConvertTo-Json
   Invoke-RestMethod -Uri "https://services.leadconnectorhq.com/hooks/RnK4OjX0oDcqtWw0VyLr/webhook-trigger/0c38f94b-57ca-4e27-94cf-4d75b55602cd" -Method POST -Body $body -ContentType "application/json"
#>

# ============================================================
# CANONICAL NUMBERS (SOURCE OF TRUTH)
# ============================================================
#
# Voice (Vapi): +1 (863) 213-2505
# Text (GHL):   +1 (352) 758-5336
#
# Dashboard:    https://www.aiserviceco.com/dashboard.html
# Modal API:    https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run
