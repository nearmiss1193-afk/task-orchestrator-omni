# Reliability Operating Procedure

> 5-minute daily checklist for AI Service Co operational health

---

## ⚡ Daily 5-Minute Checklist

```powershell
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified

# 1. Run ops autofix (checks everything)
.\scripts\ops_autofix.ps1

# 2. Quick SMS health (if Modal up)
curl.exe -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/sms/health"

# 3. Visual check
Start-Process "https://www.aiserviceco.com/dashboard.html"
```

---

## ✅ GREEN Conditions

| Check | Expected |
|-------|----------|
| `ops_autofix.ps1` | All checks PASSED |
| Modal /health | `{"status":"ok"}` |
| brand.json sync | Local sha = Production sha |
| verify_production.py | Status: GREEN or YELLOW |
| Dashboard Truth Strip | All indicators green |

---

## 🔴 RED Conditions + Fixes

### Vercel Stale (brand.json not syncing)

**Symptoms:**

- Production brand.json sha != local sha
- verify_production.py shows mismatch

**Fix:**

```
1. Go to: https://vercel.com/dashboard
2. Find empire-unified project
3. Deployments → Latest → "..." → Redeploy
4. UNCHECK "Use existing build cache"
5. Wait 60 seconds, run ops_autofix.ps1 again
```

### Modal Blocked (API not responding)

**Symptoms:**

- /health returns error or times out
- "modal-http: invalid function call"

**Fix:**

```
1. Go to: https://modal.com/apps/nearmiss1193-afk
2. Delete ALL apps with scheduled functions
3. Run: python -m modal deploy modal_orchestrator_v3.py
4. Verify: curl.exe -s .../health
```

### SMS Broken (no replies)

**Symptoms:**

- Inbound SMS received but no reply
- GHL workflow shows "Skip sending"

**Fix:**

```
1. Check GHL workflow is active
2. Verify webhook URL is correct
3. Check merge field syntax: {{trigger_link.outboundMessage}}
4. Run synthetic: curl.exe -s .../api/debug/sms?run_audit=1
```

---

## 📋 Copy-Paste Commands

### Verify Production

```powershell
python verify_production.py
```

### Run Synthetic SMS Audit

```powershell
curl.exe -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/debug/sms?run_audit=1"
```

### Deploy Modal

```powershell
python -m modal deploy modal_orchestrator_v3.py
```

### Force Vercel Deploy

```powershell
npx vercel --prod --force
```

### Full Ops Check

```powershell
.\scripts\ops_autofix.ps1
```

---

## 📞 Canonical Numbers

| Type | E164 | Display |
|------|------|---------|
| Voice | +18632132505 | (863) 213-2505 |
| SMS | +13527585336 | (352) 758-5336 |

---

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| Dashboard | <https://www.aiserviceco.com/dashboard.html> |
| Modal Apps | <https://modal.com/apps/nearmiss1193-afk> |
| Vercel | <https://vercel.com/dashboard> |
| GHL | <https://app.gohighlevel.com> |
