# Verification Checklist - Operator Playbook v3

> **Goal:** Validate all systems GREEN before going "Open for Business"

---

## ⚡ Quick 5-Minute Verification

```powershell
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified

# 1. Verify local brand compliance
python verify_brand.py --dir public --report

# 2. Verify production website (generates production_audit_report.json)
python verify_production.py

# 3. Check Modal API health (if deployed)
curl.exe -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health"

# 4. Check brand.json served correctly
curl.exe -s "https://www.aiserviceco.com/brand.json" | ConvertFrom-Json | Select-Object -ExpandProperty canonical
```

---

## ✅ GREEN Conditions

| Check | Command | Expected Output |
|-------|---------|-----------------|
| **Brand Compliance** | `python verify_brand.py --dir public` | `EXIT 0` + no violations |
| **Production Audit** | `python verify_production.py` | `Status: GREEN` or `YELLOW` |
| **JSON Report** | `cat production_audit_report.json` | `"status": "GREEN"` |
| **Modal Health** | `curl /health` | `{"status":"ok"}` |
| **brand.json** | `curl /brand.json` | JSON with voice/sms numbers |

---

## 🔴 RED Conditions (Fix Required)

### Forbidden Numbers Detected

```powershell
# Check report for details
cat production_audit_report.json | ConvertFrom-Json | Select-Object -ExpandProperty errors

# Fix the HTML files and redeploy
npx vercel --prod --force
python verify_production.py
```

### Modal API Not Responding

```powershell
# 1. Delete old Modal apps at https://modal.com/apps
# 2. Redeploy
python -m modal deploy modal_orchestrator_v3.py
```

### Brand Verification Failed

```powershell
# Check what's wrong
python verify_brand.py --dir public --report

# Auto-fix if possible
python verify_brand.py --dir public --fix

# Commit and deploy
git add -A && git commit -m "🔧 Fix brand numbers"
git push origin main
npx vercel --prod --force
```

---

## 🔒 Truth Guardrails v3

### A) Runtime Brand Injection

- Fetches `/brand.json?ts=<timestamp>` (cache-busted)
- Runs on `DOMContentLoaded` + `setTimeout(1000)` backup
- Updates `[data-brand="voice"]` and `[data-brand="sms"]` elements
- Emits to `/api/event` on failure (non-blocking)

### B) Production Verifier

- Auto-discovers all `public/*.html` pages
- Checks forbidden patterns from `brand.json`
- Validates canonical numbers on required pages
- Outputs `production_audit_report.json`

### C) Post-Deploy Alarm (GitHub Action)

- Runs after brand-verify workflow completes
- Runs hourly as drift detection
- Creates GitHub issue on failure
- Sends email alert via Resend

### D) Brand Drift Deadman (Modal - when deployed)

- Scheduled check every 30 minutes
- Fetches brand.json + homepage
- Emits `brand.drift.pass/fail` events
- Sends email alert on failure

---

## 📋 Pre-Deploy Checklist

- [ ] `python verify_brand.py --dir public` → EXIT 0
- [ ] `git status` → working tree clean
- [ ] `git push origin main` → success
- [ ] `npx vercel --prod` → deployment success
- [ ] `python verify_production.py` → Status: GREEN or YELLOW

---

## 🔐 Key URLs

| Resource | URL |
|----------|-----|
| Dashboard | <https://www.aiserviceco.com/dashboard.html> |
| brand.json | <https://www.aiserviceco.com/brand.json> |
| Modal Apps | <https://modal.com/apps/nearmiss1193-afk> |

---

## 📞 Canonical Numbers

| Type | E164 | Display |
|------|------|---------|
| Voice | +18632132505 | (863) 213-2505 |
| SMS | +13527585336 | (352) 758-5336 |
