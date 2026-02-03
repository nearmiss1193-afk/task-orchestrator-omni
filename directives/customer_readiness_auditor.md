# Customer-Side Readiness Auditor

> Detect and alert on anything that would cause a real customer to be missed.

## Mission

Ensure SMS, calls, and forms never fail silently. Provide immediate fix paths.

---

## Required Checks

### 1. SMS Pipeline

```powershell
# Health check
curl.exe -s "API_URL/api/sms/health"
```

**Require:**

- `sms_pipeline_healthy = true`
- `unreplied_count_60s = 0`

```powershell
# Synthetic test
curl.exe -s "API_URL/api/debug/sms?run_audit=1"
```

**Require:** `PASS`

### 2. Routing Truth

```powershell
curl.exe -s "API_URL/api/routing/truth"
```

**Require:** Matches `brand.json` numbers

### 3. Website Truth

```powershell
python verify_production.py
```

**Require:** No forbidden patterns on homepage + dashboard

### 4. GHL Workflow Sanity

If real inbound SMS exists but no send event within 60s:

- Emit `incident.deadman`
- Send alert email
- Output exact GHL workflow merge-field fix

---

## Output Format

```
STATUS: GREEN / YELLOW / RED

EVIDENCE:
- Last SMS inbound: [timestamp]
- Last SMS reply sent: [timestamp]
- Deadman gap: [seconds]

NEXT ACTION:
[exact command or workflow step]

REPLAY TEST:
[curl command to test fix]
```

---

## Launch Readiness Checklist

### Pre-Launch (Run Once)

- [ ] `/api/sms/health` returns `healthy: true`
- [ ] `/api/debug/sms?run_audit=1` returns `PASS`
- [ ] `verify_production.py` returns `GREEN`
- [ ] Homepage shows correct voice/sms numbers
- [ ] Dashboard shows correct voice/sms numbers
- [ ] GHL workflow triggered (test inbound SMS)
- [ ] Reply received within 60 seconds

### Hourly During Send Windows

- [ ] SMS health check
- [ ] Deadman check (unreplied count)

### Daily

- [ ] Full production audit
- [ ] Event log review for incidents

---

## One Real SMS Test Playbook

### Step 1: Send Test Inbound

```
Text "+13527585336" from your phone:
"This is a test from [your name]"
```

### Step 2: Verify Reply

- Reply should arrive within 60 seconds
- Check `event_log_v2` for:
  - `sms.inbound`
  - `sms.reply.generated`
  - `sms.reply.sent`

### Step 3: Check for Gaps

```sql
SELECT event_type, created_at 
FROM event_log_v2 
WHERE event_type LIKE 'sms.%'
ORDER BY created_at DESC 
LIMIT 10;
```

### Step 4: If No Reply

1. Check GHL workflow is active
2. Check Modal API is responding
3. Check webhook URL is correct
4. Run `/api/debug/sms?run_audit=1`

---

## Deadman Alert Template

```
🚨 DEADMAN ALERT

SMS Inbound: [timestamp]
Expected Reply By: [timestamp + 60s]
Actual Reply: NONE

Likely Cause:
[ ] GHL workflow not triggered
[ ] Modal API down
[ ] Webhook URL incorrect

Fix Steps:
1. Check GHL workflow status
2. Verify Modal health
3. Test with synthetic: /api/debug/sms?run_audit=1
```
