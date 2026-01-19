# Launch Readiness Auditor Runbook

## Overview

Autonomous monitoring system ensuring customer-facing surfaces never silently fail.

## Scheduled Jobs

| Job | Schedule | Purpose |
|-----|----------|---------|
| `scheduled_sms_synthetic` | Every 10 min | Test AI reply generation |
| `scheduled_sms_deadman` | Every 2 min | Detect unreplied SMS |
| `scheduled_website_monitor` | Every 10 min | Check phone numbers on website |

## Event Types

| Event | Severity | Meaning |
|-------|----------|---------|
| `sms.synthetic.pass` | info | AI reply generated correctly |
| `sms.synthetic.fail` | error | AI reply failed |
| `deadman.heartbeat` | info | SMS pipeline healthy |
| `incident.deadman` | error | Unreplied SMS detected |
| `website_monitor.pass` | info | Website numbers correct |
| `incident.website_number_mismatch` | error | Wrong phone on website |

## Verification SQL

```sql
-- Check recent monitor events
SELECT ts, type, severity, payload
FROM event_log_v2
WHERE type IN (
  'sms.synthetic.pass', 'sms.synthetic.fail',
  'deadman.heartbeat', 'incident.deadman',
  'website_monitor.pass', 'incident.website_number_mismatch'
)
ORDER BY ts DESC
LIMIT 20;

-- GREEN conditions (all should be true)
SELECT
  (SELECT COUNT(*) FROM event_log_v2 WHERE type = 'incident.deadman' AND ts > NOW() - INTERVAL '1 hour') = 0 as no_deadman,
  (SELECT COUNT(*) FROM event_log_v2 WHERE type = 'sms.synthetic.fail' AND ts > NOW() - INTERVAL '1 hour') = 0 as synthetic_passing,
  (SELECT COUNT(*) FROM event_log_v2 WHERE type LIKE 'incident.%' AND ts > NOW() - INTERVAL '1 hour') = 0 as no_incidents;
```

## Manual Verification

```powershell
# 1. Check SMS reply generation
$body = '{"phone":"+15551234567","message":"SYNTHETIC_TEST please reply"}'
Invoke-RestMethod -Uri "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/reply-text" -Method POST -Body $body -ContentType "application/json"

# 2. Check SMS health
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/health"

# 3. Check routing truth
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/routing/truth"
```

## Alert Escalation

1. **Yellow Alert** - sms.synthetic.fail once
   - Action: Check Gemini API key

2. **Red Alert** - incident.deadman
   - Action: Check GHL workflow execution logs
   - Fix: Verify "Save Response" enabled, test merge fields

3. **Critical** - incident.website_number_mismatch
   - Action: Fix phone numbers on website
   - Deploy: `vercel --prod`
