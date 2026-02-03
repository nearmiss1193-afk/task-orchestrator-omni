# Launch Verification Runbook

## GREEN Status Before Launch

Run these commands and verify all checks pass.

### 1. Brand Compliance (Website Numbers)

```powershell
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified
python verify_brand.py --dir public --json
```

✅ **Expected:** `"passed": true`

### 2. Modal Health

```powershell
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health" | ConvertTo-Json
```

✅ **Expected:** `"status": "ok"`

### 3. Auditor Truth (Full System Status)

```powershell
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/auditor/truth" | ConvertTo-Json -Depth 4
```

✅ **Expected:**

```json
{
  "status": "ok",
  "sms_pipeline_healthy": true,
  "health_reasons": [],
  "unreplied_count_60s": 0,
  "synthetic_last_status": "pass"
}
```

### 4. Routing Truth (Canonical Numbers)

```powershell
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/routing/truth" | ConvertTo-Json
```

✅ **Expected:**

- `canonical_voice_number: "+18632132505"`
- `canonical_sms_number: "+13527585336"`

### 5. Synthetic SMS Audit (On-Demand)

```powershell
Invoke-RestMethod "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/debug/sms?run_audit=1" | ConvertTo-Json -Depth 4
```

✅ **Expected:** `"audit_result": { "status": "PASS" }`

---

## GREEN Checklist

| Check | Command Suffix | Pass Criteria |
|-------|----------------|---------------|
| Brand | `verify_brand.py --dir public --json` | `passed: true` |
| Modal | `/health` | `status: ok` |
| Auditor | `/api/auditor/truth` | `sms_pipeline_healthy: true` |
| Routing | `/api/routing/truth` | Canonical numbers correct |
| Synthetic | `/api/debug/sms?run_audit=1` | `audit_result.status: PASS` |

---

## If Something Is RED

| Issue | Check | Fix |
|-------|-------|-----|
| `sms_pipeline_healthy: false` | Look at `health_reasons` | See `synthetic_failed` or `unreplied_X` |
| `synthetic_failed` | Check Gemini API key | Verify GEMINI_API_KEY in Modal secrets |
| `unreplied_X` | Check GHL workflow | See `runbooks/ghl_sms_troubleshooting.md` |
| `brand passed: false` | Run `--fix` | `python verify_brand.py --dir public --fix` |

---

## Canonical Numbers

| Label | Number | Provider |
|-------|--------|----------|
| **VOICE** | (863) 213-2505 | Vapi |
| **TEXT** | (352) 758-5336 | GHL |
