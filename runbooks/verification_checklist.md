# Launch Readiness Verification Checklist

Execute these commands to verify the system is GREEN.

## 1. PowerShell Verification Commands

```powershell
$BaseUrl = "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run"

# Test 1: Health
Write-Host "[1] Testing /health..."
Invoke-RestMethod "$BaseUrl/health" | ConvertTo-Json

# Test 2: Routing Truth
Write-Host "[2] Testing /api/routing/truth..."
Invoke-RestMethod "$BaseUrl/api/routing/truth" | ConvertTo-Json

# Test 3: SMS Reply Generation
Write-Host "[3] Testing /api/sms/reply-text..."
$body = '{"phone":"+15551234567","message":"I need help with AI automation"}'
Invoke-RestMethod "$BaseUrl/api/sms/reply-text" -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json

# Test 4: SMS Health
Write-Host "[4] Testing /api/sms/health..."
Invoke-RestMethod "$BaseUrl/api/sms/health" | ConvertTo-Json

# Test 5: Debug SMS with Audit
Write-Host "[5] Running Synthetic Audit..."
Invoke-RestMethod "$BaseUrl/api/debug/sms?run_audit=1" | ConvertTo-Json -Depth 4
```

## 2. Supabase SQL Verification

```sql
-- Recent SMS events
SELECT type, severity, ts, entity_id, correlation_id
FROM event_log_v2
WHERE type IN ('sms.inbound', 'sms.reply.generated', 'sms.reply.sent')
ORDER BY ts DESC
LIMIT 20;

-- Synthetic pass/fail events
SELECT type, ts, payload
FROM event_log_v2
WHERE type LIKE 'sms.synthetic%'
ORDER BY ts DESC
LIMIT 10;

-- Deadman incidents
SELECT type, ts, severity, payload
FROM event_log_v2
WHERE type = 'incident.deadman'
ORDER BY ts DESC
LIMIT 5;

-- All auditor events
SELECT type, ts, severity, payload
FROM event_log_v2
WHERE source = 'auditor'
ORDER BY ts DESC
LIMIT 20;
```

## 3. GREEN Condition Definition

| Metric | GREEN Threshold |
|--------|-----------------|
| `/api/sms/health` | `sms_pipeline_healthy: true` |
| `unreplied_count_60s` | = 0 |
| Last `sms.synthetic.pass` | Within 15 minutes |
| Last `incident.deadman` | None in 1 hour |
| Last `sms.reply.sent` | Within 30 minutes (if active) |
| Website canonical numbers | Both present |

## 4. RED Actions

| Condition | Action |
|-----------|--------|
| `sms.synthetic.fail` | Check Gemini API key, check Modal secrets |
| `incident.deadman` | Check GHL workflow, verify "Save Response" enabled |
| `sms_pipeline_healthy: false` | Check /api/debug/sms, review unreplied count |
| Wrong number on website | Run `python verify_brand.py --dir public --fix` |

## 5. Brand Governor Check

```powershell
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified
python verify_brand.py --dir public --json
```

Expected: `"passed": true`
