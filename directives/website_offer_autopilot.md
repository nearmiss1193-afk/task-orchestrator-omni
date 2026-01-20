# Website + Offer Autopilot

> Keeps all public pages correct and improves conversion via controlled testing.

## Goals

1. Keep all public pages **ALWAYS correct** (numbers, offers, CTA labels)
2. Improve conversion weekly via small tests
3. Never drift from canonical truth

---

## Truth Sources

| Source | Purpose |
|--------|---------|
| `brand.json` | Canonical phone numbers and labels |
| `BRAND_CANON.md` | Canonical messaging |
| `verify_brand.py` | Pre-deploy gate |
| `verify_production.py` | Post-deploy gate |

---

## Scope

### May Edit

- `public/*.html`
- `public/audits/*.html`
- `public/assets/**`

### May NOT Edit

- backups/
- manifests/
- runbooks/
- sql/
- Internal scripts (unless asked)

---

## Auto-Fix Rules (Always On)

On every change, run:

```powershell
# Fix any violations
python verify_brand.py --dir public --fix

# Verify clean
python verify_brand.py --dir public --json

# Check production (must be GREEN)
python verify_production.py
```

If violations remain: **STOP** and output patch + explanation.

---

## Weekly Conversion Loop

1. **Pick ONE page**
2. **Propose ONE test:**
   - Headline
   - CTA
   - Proof block
   - Pricing framing
3. **Include measurement plan:**
   - Visitors (if available)
   - Clicks
   - Form submits
   - Booked calls
4. **Do NOT change pricing** without explicit approval

---

## Deliverable Format

```
1. CHANGE PLAN (what and why)
2. UNIFIED DIFF PATCH
3. VERIFICATION COMMANDS
4. ROLLBACK PLAN
```

---

## Scan Report Template

On startup, scan `public/` and report:

1. **Number/Label Consistency**
   - Voice: +18632132505 / (863) 213-2505
   - SMS: +13527585336 / (352) 758-5336

2. **Offer Consistency**
   - Pricing matches brand.json
   - CTAs match BRAND_CANON.md

3. **Top 3 Conversion Improvements** (no code yet)
   - Opportunity 1
   - Opportunity 2
   - Opportunity 3
