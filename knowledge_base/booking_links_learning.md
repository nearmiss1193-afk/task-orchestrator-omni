# Critical Learning: Booking Links Strategy

Date: 2026-01-09

## Problem Identified

**All Calendly links (`calendly.com/aiserviceco/demo`) are returning 404 errors.**

This means every prospect who clicked our "Book a Call" CTA hit a dead end!

## Root Cause

- Calendly account may not exist or link was never configured
- Link was hardcoded across 50+ files without verification

## Solution Implemented

Replace all Calendly links with working website URLs:

- **Primary CTA**: `https://www.aiserviceco.com/features.html`
- **Why**: Better experience - shows AI capabilities, builds trust, has contact info

## Files That Need Updates

1. hvac_campaign.py ✅ FIXED
2. send_premium_email.py
3. send_test_spear.py  
4. sms_blast_4pm.py
5. scale_100_campaign.py
6. run_spear_campaign.py
7. send_prospect_email.py
8. deploy_final_sso.py
9. modules/constructor/page_builder.py
10. modules/orchestrator/deploy.py

## Recommended CTA Text Changes

- OLD: "📞 Book a Quick Chat"
- NEW: "📞 See How It Works" or "📞 Watch Demo"

## Prevention Rules for Future

1. Never use external booking links without testing them first
2. Prefer internal landing pages over third-party booking tools
3. Add link verification to pre-flight campaign checks

## Why This Wasn't Caught Earlier

- No automated link checker in deploy pipeline
- Dashboard didn't surface failed clicks (no analytics)
- Campaigns were sending but outcomes weren't tracked

## Recommendation

Add to automated audit checklist:

- [ ] Verify all CTA links return 200 OK before campaign launch
- [ ] Track click-through rates to identify silent failures
