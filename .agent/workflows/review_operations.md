---
description: Review operations - full system health check and status report
---

# Review Operations

// turbo-all

When the user runs `/review_operations`, execute a full operational review:

## Steps

1. **Check Modal App Status**

   ```
   python -m modal app list --json
   ```

   Verify only `ghl-omni-automation` is running. Flag any crash-looping or stale apps.

2. **Check CRON Count** — Must be ≤ 5:

   ```
   Select-String -Path deploy.py -Pattern "schedule=modal"
   ```

3. **Query Database Health** — Run these checks against Supabase:
   - `outbound_touches` — count in last 30 min (outreach active?)
   - `system_health_log` — last heartbeat timestamp
   - `system_state` — campaign_mode = 'working'?
   - `contacts_master` — status distribution (any contactable leads?)

4. **Check Lead Queue** — Are there leads with status 'new' or 'research_done'?
   If queue is empty, flag as critical.

5. **Generate Report** — Output in this format:

   ```
   ══════════════════════════════════════
   OPERATIONS REVIEW - [timestamp]
   ══════════════════════════════════════
   Modal App:      [✅/❌] [app name]
   CRONs:          [N]/5
   Heartbeat:      [✅/❌] last: [time]
   Campaign Mode:  [✅/❌] [value]
   Outreach (30m): [✅/❌] [count] sent
   Lead Queue:     [✅/❌] [count] contactable
   
   STATUS: [ALL CLEAR / DEGRADED / CRITICAL]
   ══════════════════════════════════════
   ```
