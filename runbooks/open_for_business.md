# Open For Business Runbook

## 🚀 Launch Day Commands (Run This Now)

### Step 1: Verify Brand Compliance

```powershell
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified
python verify_brand.py --dir public --report
```

Expected: `PASSED - All phone numbers are canonical`

### Step 2: Auto-Fix Any Violations (if needed)

```powershell
python verify_brand.py --dir public --fix
python verify_brand.py --dir public --json
```

Expected: `"passed": true`

### Step 3: Check Modal Health

```powershell
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health" | ConvertTo-Json
```

Expected: `"status": "ok"`

### Step 4: Check SMS Health

```powershell
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/health" | ConvertTo-Json
```

Expected:

```json
{
  "status": "ok",
  "sms_pipeline_healthy": true,
  "unreplied_count_60s": 0
}
```

### Step 5: Check Routing Truth

```powershell
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/routing/truth" | ConvertTo-Json
```

Expected:

```json
{
  "canonical_voice_number": "+18632132505",
  "canonical_sms_number": "+13527585336"
}
```

### Step 6: Run Synthetic SMS Audit

```powershell
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/debug/sms?run_audit=1" | ConvertTo-Json -Depth 4
```

Expected: `"audit_result": { "status": "PASS" }`

### Step 7: Deploy Modal (if changes made)

```powershell
python -m modal deploy modal_orchestrator_v3.py
```

### Step 8: Deploy to Vercel (if website changes)

```powershell
vercel --prod
```

---

## ✅ GREEN Checklist (Launch Readiness)

| Check | Command | Expected |
|-------|---------|----------|
| Brand Compliance | `python verify_brand.py --dir public --json` | `"passed": true` |
| Modal Health | GET `/health` | `status: ok` |
| SMS Health | GET `/api/sms/health` | `sms_pipeline_healthy: true` |
| Routing Truth | GET `/api/routing/truth` | Voice: +18632132505, SMS: +13527585336 |
| Synthetic Audit | GET `/api/debug/sms?run_audit=1` | `audit_result.status: PASS` |
| GHL Workflow | Check Execution Logs | No "Skip sending" errors |

---

## 📊 Supabase Event Verification

```sql
-- Recent SMS events (last 1 hour)
SELECT type, ts, entity_id, correlation_id
FROM event_log_v2
WHERE type IN ('sms.inbound', 'sms.reply.generated', 'sms.reply.sent')
  AND ts > NOW() - INTERVAL '1 hour'
ORDER BY ts DESC
LIMIT 20;

-- Synthetic audit events
SELECT type, ts, payload
FROM event_log_v2
WHERE type LIKE 'sms.synthetic%'
ORDER BY ts DESC
LIMIT 10;

-- Deadman incidents (should be empty if healthy)
SELECT type, ts, severity, payload
FROM event_log_v2
WHERE type = 'incident.deadman'
  AND ts > NOW() - INTERVAL '24 hours'
ORDER BY ts DESC;
```

---

## 🔴 If Something Is Broken

### SMS Not Working

1. Check `/api/sms/health` → look at `last_error`
2. Check `/api/debug/sms` → look at `ghl_errors`
3. See runbook: `runbooks/ghl_sms_troubleshooting.md`

### Wrong Phone Numbers on Website

```powershell
python verify_brand.py --dir public --fix
vercel --prod
```

### Modal Not Responding

```powershell
python -m modal deploy modal_orchestrator_v3.py
```

### Deadman Alerts Firing

1. Check GHL Execution Logs for workflow failures
2. Verify "Save response" checkbox enabled on webhook step
3. Test merge field syntax (see `runbooks/ghl_sms_troubleshooting.md`)

---

## 📞 Canonical Numbers

| Label | Display | E164 | Provider |
|-------|---------|------|----------|
| **VOICE** | (863) 213-2505 | +18632132505 | Vapi |
| **TEXT** | (352) 758-5336 | +13527585336 | GHL |

---

## 🔗 Quick Links

- **Dashboard**: <https://www.aiserviceco.com/dashboard.html>
- **GHL**: <https://app.gohighlevel.com>
- **Modal**: <https://modal.com/apps>
- **Supabase**: <https://supabase.com/dashboard>
- **Vapi**: <https://dashboard.vapi.ai>
