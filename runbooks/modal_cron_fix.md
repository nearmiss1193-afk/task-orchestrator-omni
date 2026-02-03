# Modal Cron Limit Fix Runbook

> [!CAUTION]
> Modal free tier allows **5 scheduled functions (cron jobs) per workspace**.
> If you exceed this, all deploys fail with "reached limit of 5 cron jobs".

## Symptoms

Deploy command fails with:

```
Deployment failed: reached limit of 5 cron jobs
(# already deployed => 5, # in this app => X)
Please upgrade your workspace plan and re-deploy
```

## Root Cause

Old Modal apps from previous deployments still have scheduled functions registered.
Even if the app is "stopped", the cron registrations persist.

## Fix Steps (5 min)

### Step 1: Identify Apps with Crons

```bash
python -m modal app list
```

Or go to: <https://modal.com/apps/nearmiss1193-afk>

### Step 2: Delete Old Apps

For each app that is NOT `empire-api-v3`, delete it:

```bash
# List apps
python -m modal app list

# Stop old apps (replace APP_NAME with actual names)
python -m modal app stop empire-api-v1
python -m modal app stop empire-api-v2
python -m modal app stop empire-webhooks
python -m modal app stop empire-orchestrator
```

Or via dashboard:

1. Go to <https://modal.com/apps>
2. Click each old app
3. Click Settings → Delete App

### Step 3: Verify Cron Count

After deleting, the count should be < 5:

```bash
python -m modal app list
```

### Step 4: Redeploy

```bash
cd C:\Users\nearm\.gemini\antigravity\scratch\empire-unified
python -m modal deploy modal_orchestrator_v3.py
```

### Step 5: Verify Deployment

```bash
curl https://nearmiss1193-afk--empire-api-v3-orchestration-api.modal.run/api/truth
```

Should return JSON with `server_ts`, `last_event_ts`, etc.

## Prevention

Keep only ONE production Modal app deployed.
All other functions should be event-driven, not scheduled.

## Escalation

If you need more than 5 crons, upgrade at:
<https://modal.com/settings/nearmiss1193-afk/plans>
