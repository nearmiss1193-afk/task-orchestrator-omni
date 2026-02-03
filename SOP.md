# EMPIRE STANDARD OPERATING PROCEDURES (SOP)

## Last Updated: 2026-01-12

---

## 1. LEAD ENRICHMENT SOP (Self-Healing)

### Problem Solved

AI-generated leads often have fake 555 phone numbers, causing 0% call success.

### Current System

1. **`lead_quality_guardian.py`** - Runs before campaigns to:
   - Validate all phone numbers (reject 555, too short)
   - Auto-enrich via Apollo.io for decision maker data
   - Mark failures for manual review

2. **`cloud_multi_touch`** (Modal) - Includes:
   - Pre-flight quality validation
   - On-the-fly Apollo enrichment for invalid phones
   - Phone priority: `enriched_phone > phone field > agent_research`

### APIs Used

| API | Purpose | Status |
|-----|---------|--------|
| Apollo.io | Decision maker lookup, phone/email | ✅ ACTIVE |
| Hunter.io | Email verification | ✅ CONFIGURED |
| Manus/Grok | Deep research backup | ✅ KEY SAVED |

### Run Manually

```bash
python lead_quality_guardian.py  # Validate & enrich leads
python -m modal run modal_deploy.py::cloud_multi_touch  # Send emails + calls
```

---

## 2. CAMPAIGN SCHEDULE (Modal Cloud)

| Function | Schedule | Description |
|----------|----------|-------------|
| `cloud_drip_campaign` | 9 AM daily | Follow-up drip emails |
| `cloud_prospector` | Every 4 hours | Hunt new HVAC leads |
| `cloud_multi_touch` | 10 AM, 2 PM daily | Email + Call outreach |
| `self_healing_monitor` | Every 30 min | Health check + auto-repair |
| `social_media_poster` | 8 AM daily | AI social posts via Ayrshare |
| `social_media_analytics` | 10 PM daily | Collect social stats |

---

## 3. DASHBOARD REAL-TIME STATUS

### Data Sources (Supabase)

- **Calls**: `call_transcripts` table - updated via Vapi webhook
- **Emails**: `email_logs` table - updated via Resend webhook
- **Leads**: `leads` table - updated by prospector/enrichment

### Update Frequency

- Vapi webhook: **Real-time** (on call end)
- Dashboard polling: **30 second refresh** (JavaScript)
- Supabase: **Instant** (PostgREST API)

### Check Dashboard

```
https://aiserviceco.com/dashboard.html
```

---

## 4. SAVE PROTOCOL

### What Gets Saved

1. All code changes to Git
2. Environment variables secured in .env
3. Modal secrets synced from .env
4. System logs to Supabase

### Run Save Protocol

```bash
# 1. Stage all changes
git add -A

# 2. Commit with timestamp
git commit -m "Save Protocol: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

# 3. Push to backup
git push backup main

# 4. Deploy to Modal (if needed)
python -m modal deploy modal_deploy.py
```

---

## 5. TROUBLESHOOTING

### No Calls Being Made

1. Check `system_logs` for CLOUD_OUTREACH events
2. Verify leads have valid phones: `python lead_quality_guardian.py`
3. Check Vapi assistant ID exists
4. Verify VAPI_PRIVATE_KEY and VAPI_PHONE_NUMBER_ID in .env

### Dashboard Not Updating

1. Check browser console for errors
2. Verify Supabase URL/Key in dashboard.html
3. Check Vapi webhook URL is registered

### Apollo Enrichment Failing

1. Verify APOLLO_API_KEY in .env
2. Check API credits at app.apollo.io
3. Try Hunter.io as fallback

---

## 6. KEY FILES

| File | Purpose |
|------|---------|
| `modal_deploy.py` | Main cloud deployment (13 functions) |
| `lead_quality_guardian.py` | Self-healing lead enrichment |
| `hunter_apollo_integration.py` | Enrichment APIs |
| `health_monitor.py` | Local health check |
| `.env` | All API keys and secrets |

---

*Empire Sovereign System v2.0*
