# Directive: System Integrity Guardian

## Goal

Self-maintaining monitor to ensure 100% uptime and automatic error recovery.

## Execution (health_check.py)

- **Schedule**: Every 4 hours via Modal Cron.
- **API Verify**: Ping GHL, Supabase, and Gemini endpoints.
- **Stuck Lead Check**: Identify leads in 'processing' status for > 30 minutes.
- **Self-Repair**:
  - If a lead is stuck, re-trigger scanning with a different proxy or search engine.
  - If logs indicate an API schema change, flag for orchestration update.

## Process

1. Run `health_check.py`.
2. Parse JSON results.
3. If errors found: Auto-redeploy Modal app with updated environment/fixes.
4. Notify admin if manual intervention is required.
