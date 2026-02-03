# Jan 18 HVAC Kickoff Runbook
# PowerShell commands for verification and testing

# =====================================================
# SECTION C1: VERIFY SYSTEM STATUS
# =====================================================

# Health check
curl -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health" | ConvertFrom-Json | ConvertTo-Json -Depth 5

# Marketing status (autopost should be OFF)
curl -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/marketing/status" | ConvertFrom-Json | ConvertTo-Json -Depth 5

# Kickoff status (should show kickoff_scheduled_for_tomorrow=true, readiness=GO)
curl -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/kickoff/status" | ConvertFrom-Json | ConvertTo-Json -Depth 5

# Reliability check (kickoff.deadman check)
curl -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/reliability-check" | ConvertFrom-Json | ConvertTo-Json -Depth 5

# Learning metrics (variant performance)
curl -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/learning-metrics" | ConvertFrom-Json | ConvertTo-Json -Depth 5

# =====================================================
# SECTION C2: DRY RUN TEST (1 fake contact)
# =====================================================

$dryRunPayload = @{
    contacts = @(
        @{
            phone    = "+15551234567"
            company  = "TestHVAC Co"
            vertical = "hvac"
            timezone = "America/Chicago"
            touch    = 1
            channel  = "sms"
        }
    )
    dry_run  = $true
    run_id   = "test_dry_run_jan17"
} | ConvertTo-Json -Depth 5

curl -X POST "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/campaign-batch" -H "Content-Type: application/json" -d $dryRunPayload

# =====================================================
# SECTION C3: LIVE FIRE TEST (5 contacts max)
# =====================================================
# WARNING: This sends REAL SMS messages!
# Only run when ready to test with real contacts

$livePayload = @{
    contacts = @(
        @{
            phone    = "+1REAL_PHONE_1"
            company  = "Real HVAC Company 1"
            vertical = "hvac"
            timezone = "America/Chicago"
            touch    = 1
            channel  = "sms"
            id       = "contact_001"
        },
        @{
            phone    = "+1REAL_PHONE_2"
            company  = "Real HVAC Company 2"
            vertical = "hvac"
            timezone = "America/Chicago"
            touch    = 1
            channel  = "sms"
            id       = "contact_002"
        }
        # Add up to 5 contacts
    )
    dry_run  = $false
    run_id   = "jan18_live_test_001"
} | ConvertTo-Json -Depth 5

# Uncomment to run:
# curl -X POST "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/campaign-batch" -H "Content-Type: application/json" -d $livePayload

# =====================================================
# SECTION C4: SUPABASE VERIFICATION QUERIES
# Run these in Supabase SQL Editor after testing
# =====================================================

# --- Verify event_log_v2 receiving events ---
# SELECT type, source, severity, correlation_id, ts 
# FROM event_log_v2 
# WHERE ts > NOW() - INTERVAL '1 hour'
# ORDER BY ts DESC LIMIT 20;

# --- Verify job_runs records ---
# SELECT job_name, window_id, status, scheduled_for, ts
# FROM job_runs
# WHERE scheduled_for >= '2026-01-17'
# ORDER BY ts DESC LIMIT 10;

# --- Verify outreach_attribution records ---
# SELECT phone, channel, variant_id, variant_name, correlation_id, ts
# FROM outreach_attribution
# ORDER BY ts DESC LIMIT 20;

# --- Check for kickoff events ---
# SELECT type, payload, ts
# FROM event_log_v2
# WHERE type LIKE 'kickoff.%' OR type LIKE 'campaign.%'
# ORDER BY ts DESC LIMIT 20;

# =====================================================
# SECTION D: SAFETY SWITCHES
# =====================================================

# Outreach Kill Switch:
# - OUTREACH_ENABLED=false → /api/campaign-batch returns "disabled" with campaign.disabled event
# - Default: true (outreach enabled)
# - To disable: modal secret update empire-secrets OUTREACH_ENABLED=false

# Content Engine Kill Switch:
# - MARKETING_AUTOPOST_ENABLED=false → posting_rules all disabled
# - Default: false (autopost disabled)
# - All posting_rules start with enabled=false

# =====================================================
# SECTION E: JAN 18 MORNING CHECKLIST
# =====================================================

# 1. Check kickoff status (should show readiness=GO)
curl -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/kickoff/status" | ConvertFrom-Json

# 2. Check reliability (should be healthy, no incidents)
curl -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/reliability-check" | ConvertFrom-Json

# 3. Monitor event_log_v2 for:
#    - kickoff.scheduled (should appear when /api/kickoff/status is called)
#    - campaign.batch.started
#    - campaign.batch.completed
#    - kickoff.started (first batch of the day)

# 4. If by 10am CT no batches run, reliability-check will emit:
#    - incident.deadman with type="kickoff_missed"
#    - kickoff.catchup event

# 5. To manually trigger catchup, run live fire test with real contacts

# =====================================================
# DEPLOY UPDATED CODE
# =====================================================

# From empire-unified directory:
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified
modal deploy modal_orchestrator.py

# Verify deployment:
curl -s "https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/health"
