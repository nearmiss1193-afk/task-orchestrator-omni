# Verification Checklist - Operator Playbook

> **Goal:** Validate all systems GREEN before going "Open for Business"

---

## ⚡ Quick 5-Minute Verification

```powershell
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified

# 1. Verify local brand compliance
python verify_brand.py --dir public --report

# 2. Verify production website
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
| **Production Site** | `python verify_production.py` | `Status: GREEN` |
| **Modal Health** | `curl /health` | `{"status":"ok"}` |
| **brand.json** | `curl /brand.json` | JSON with voice_number_e164 |
| **Sarah AI** | Call +1 (863) 213-2505 | Sarah answers |

---

## 🔴 RED Conditions (Fix Required)

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

# If fixable, auto-fix
python verify_brand.py --dir public --fix

# Commit and deploy
git add -A && git commit -m "🔧 Fix brand numbers"
git push origin main
npx vercel --prod --force
```

### Production Shows Wrong Numbers

```powershell
# Force cache purge
npx vercel --prod --force

# Wait 60s, then verify
python verify_production.py
```

---

## 📋 Pre-Deploy Checklist

- [ ] `python verify_brand.py --dir public` → EXIT 0
- [ ] `git status` → working tree clean
- [ ] `git push origin main` → success
- [ ] `npx vercel --prod` → deployment success
- [ ] `python verify_production.py` → Status: GREEN

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
