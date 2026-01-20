# Open For Business Runbook

> [!IMPORTANT]
> This runbook ensures AIServiceCo is "operationally unbreakable" 24/7.

## Pre-Flight Checklist

### 1. Website Truth Verification

```powershell
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified

# Verify local files have correct numbers
python verify_brand.py --dir public --report

# Verify production site has correct numbers
python verify_production.py
```

**Expected:** Both scripts return GREEN.

### 2. Modal API Verification

```powershell
# Check if Modal can deploy
python -m modal deploy modal_orchestrator_v3.py

# If blocked by cron limit, see runbooks/modal_cron_fix.md
```

### 3. Dashboard Verification

```powershell
# Open and verify
Start-Process "https://www.aiserviceco.com/dashboard.html"
```

---

## GREEN Checklist

| System | Command | Expected |
|--------|---------|----------|
| Website Numbers | `python verify_production.py` | GREEN |
| brand.json | `curl https://www.aiserviceco.com/brand.json` | 200 + correct numbers |
| Modal Health | `curl https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health` | {"status":"ok"} |
| SMS Pipeline | `curl .../api/sms/health` | {"status":"ok"} |
| Sarah (Vapi) | Call +1 (863) 213-2505 | Sarah answers |

---

## Quick Fixes

### Website Shows Wrong Numbers

```powershell
python verify_brand.py --dir public --fix
git add -A && git commit -m "🔧 Fix phone numbers"
git push origin main
npx vercel --prod --force
python verify_production.py
```

### Modal Cron Limit

See: `runbooks/modal_cron_fix.md`

### SMS Not Working

1. Check GHL workflow is active
2. Check Modal /api/sms/health endpoint
3. Run synthetic: `curl .../api/debug/sms?run_audit=1`

---

## Canonical Numbers

| Type | Number | Display |
|------|--------|---------|
| VOICE | +18632132505 | (863) 213-2505 |
| TEXT | +13527585336 | (352) 758-5336 |

---

## Recovery Commands

```powershell
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified

# Deploy to Vercel
npx vercel --prod --force

# Deploy to Modal (after cron fix)
python -m modal deploy modal_orchestrator_v3.py

# Verify everything
python verify_production.py
```
