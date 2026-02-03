# ============================================================
# SMS LAUNCH VERIFICATION RUNBOOK - Jan 18, 2026
# Steps 0-5 for "no answer on SMS/text" fix
# ============================================================

# ============================================================
# STEP 1: GHL WORKFLOW SETUP (CRITICAL - DO THIS FIRST)
# ============================================================
<#
1. Go to GHL > Automations > Workflows > + Create Workflow
2. Choose "Start from Scratch"
3. Add Trigger: Click "+ Add Trigger"
   - Select "Customer Replied" OR "Inbound Message" (whichever exists)
   - Filter: Message Type = SMS
4. Add Action: Click "+" then "Webhook"
   - Method: POST
   - URL: https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/webhook/ghl/sms/inbound
   - Body Type: Custom JSON
   - Body (Template A - preferred):
     {
       "phone": "{{contact.phone}}",
       "message": "{{message.body}}",
       "contactId": "{{contact.id}}",
       "conversationId": "{{conversation.id}}"
     }
   
   - Body (Template B - fallback if fields differ):
     {
       "phone": "{{contact.phone_number}}",
       "message": "{{trigger.message.body}}",
       "contactId": "{{contact.contact_id}}",
       "conversationId": "{{trigger.conversation_id}}"
     }

   - Body (Template C - minimal):
     {
       "phone": "{{contact.phone}}",
       "message": "{{message.body}}"
     }

5. Save and Publish workflow
6. Test by texting +1 (352) 758-5336
#>

# ============================================================
# STEP 5: VERIFICATION COMMANDS (paste these)
# ============================================================

Write-Host "`n=== 1. CHECK ROUTING TRUTH ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/routing/truth" | ConvertTo-Json

# Expected output:
# canonical_voice_number: +18632132505 (Vapi)
# canonical_sms_number: +13527585336 (GHL)
# voice_provider: vapi
# sms_provider: ghl

Write-Host "`n=== 2. CHECK SMS HEALTH ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/health" | ConvertTo-Json

Write-Host "`n=== 3. CHECK SMS DEBUG (last 10 events) ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/debug/sms" | ConvertTo-Json -Depth 5

Write-Host "`n=== 4. SIMULATE INBOUND SMS (without GHL) ===" -ForegroundColor Cyan
$body = @{
    phone          = "+13529368152"
    message        = "Hi I need help with my AC unit"
    contactId      = "sim_test_001"
    conversationId = "sim_conv_001"
} | ConvertTo-Json
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/webhook/ghl/sms/inbound" -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json

Write-Host "`n=== 5. CHECK BASIC HEALTH ===" -ForegroundColor Cyan
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health" | ConvertTo-Json

# ============================================================
# SUPABASE VERIFICATION (run in SQL editor)
# ============================================================
<#
-- Last 50 SMS events
SELECT ts, type, entity_id as phone, severity, payload->>'method' as method
FROM event_log_v2
WHERE type LIKE 'sms.%'
ORDER BY ts DESC
LIMIT 50;

-- Deadman heartbeats
SELECT ts, type, payload->>'status' as status, payload->>'unreplied_count' as unreplied
FROM event_log_v2
WHERE type IN ('deadman.heartbeat', 'incident.deadman')
ORDER BY ts DESC
LIMIT 20;

-- Recent errors
SELECT ts, type, source, payload->>'error' as error
FROM event_log_v2
WHERE severity = 'error' AND ts > NOW() - INTERVAL '1 hour'
ORDER BY ts DESC
LIMIT 20;
#>

# ============================================================
# SUCCESS CRITERIA CHECKLIST
# ============================================================
<#
[ ] /api/routing/truth returns voice_provider=vapi, sms_provider=ghl
[ ] /api/routing/truth returns correct numbers
[ ] GHL workflow is published and active
[ ] Text to +1 (352) 758-5336 creates sms.inbound event in /api/debug/sms
[ ] AI reply sent within 60 seconds (sms.reply.sent event visible)
[ ] /api/sms/health shows unreplied_count_60s = 0
[ ] Deadman heartbeat events appear every 2 min in event_log_v2
#>

# ============================================================
# IF BROKEN, DO THIS
# ============================================================
<#
1. NO sms.inbound events in /api/debug/sms:
   -> GHL workflow not configured. Follow STEP 1 above.

2. sms.inbound exists but no sms.reply.sent:
   -> Check ghl_errors in /api/debug/sms
   -> Verify GHL_API_KEY is set in Modal secrets

3. API returning 500/errors:
   -> Redeploy: python -m modal deploy modal_orchestrator_v3.py

4. Deadman not running:
   -> Check Modal scheduled functions: python -m modal app logs empire-api-v3

5. Disable deadman temporarily:
   -> Set SMS_DEADMAN_ENABLED=false in Modal secrets
#>

# ============================================================
# CANONICAL NUMBERS (SOURCE OF TRUTH)
# ============================================================
# Voice (Call Sarah): +1 (863) 213-2505 -> Vapi
# Text (SMS Sarah):   +1 (352) 758-5336 -> GHL
#
# Dashboard: https://www.aiserviceco.com/dashboard.html
# Modal API: https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run

# ============================================================
# RECOVERY COMMANDS
# ============================================================
<#
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified
python -m modal deploy modal_orchestrator_v3.py
python -m modal app logs empire-api-v3
#>
