---
description: Aggressive 24/7 outreach pattern - calls, emails, SMS
---

# Outreach SOP - 24/7 Campaign Protocol

> [!CAUTION]
> This system runs CONTINUOUSLY. Prospecting and outreach happen around the clock
> following timezone-aware scheduling.

---

## 🎯 Core Rules

1. **Prospecting**: Runs every **15 minutes** (not 2 hours)
2. **Outreach Sequence**: Email → SMS → Call (or Call first if phone available)
3. **Calling Frequency**: No less than every **5 minutes**
4. **Call Hours**: 8 AM to 6 PM **LOCAL TIME** in target timezone
5. **Timezone Flow**: East Coast → Central → Mountain → Pacific → Hawaii → Restart

---

## ⏰ Timezone-Aware Call Windows

| Timezone | UTC Offset | Call Window (Local) | Call Window (EST) |
|----------|------------|---------------------|-------------------|
| Eastern  | UTC-5      | 8 AM - 6 PM        | 8 AM - 6 PM       |
| Central  | UTC-6      | 8 AM - 6 PM        | 9 AM - 7 PM       |
| Mountain | UTC-7      | 8 AM - 6 PM        | 10 AM - 8 PM      |
| Pacific  | UTC-8      | 8 AM - 6 PM        | 11 AM - 9 PM      |
| Hawaii   | UTC-10     | 8 AM - 6 PM        | 1 PM - 11 PM      |

**Logic**: At any given hour, determine which timezone is in call window and prioritize leads from that region.

---

## 📞 Outreach Sequence

For each lead:

```
1. IF phone exists AND within call window:
   → CALL immediately
   → Wait for result (30 sec timeout)
   
2. THEN send EMAIL (always)
   
3. THEN send SMS (if phone exists)

4. Mark lead as "contacted"

5. Wait 5 minutes minimum before next call
```

---

## 🔄 Scheduler Intervals

| Task | Interval | Hours | Description |
|------|----------|-------|-------------|
| Prospecting | Every 10 min | 24/7 | Find new companies via Apollo |
| Email Outreach | Every 3 min | **24/7** | Process new leads, send emails anytime |
| SMS Outreach | Every 3 min | Business Hours | Only during timezone call window |
| Calling | Every 3 min | Business Hours | 20 calls/hour target, timezone-aware |
| Status Report | Every 6 hours | 24/7 | Send stats to owner |

> [!IMPORTANT]
> **EMAILS run 24/7** - No timezone restriction
> **CALLS and SMS** - Only during business hours (8 AM - 6 PM local time)

---

## 🌍 Lead Priority by Time

```python
def get_priority_timezone():
    """Returns which timezone to prioritize based on current UTC hour"""
    from datetime import datetime, timezone
    utc_hour = datetime.now(timezone.utc).hour
    
    # 8 AM - 6 PM windows mapped to UTC
    # East: 13-23 UTC (8 AM - 6 PM EST)
    # Central: 14-00 UTC
    # Mountain: 15-01 UTC  
    # Pacific: 16-02 UTC
    # Hawaii: 18-04 UTC
    
    if 13 <= utc_hour < 23:
        return "Eastern"
    elif 14 <= utc_hour or utc_hour < 1:
        return "Central"
    elif 15 <= utc_hour or utc_hour < 2:
        return "Mountain"
    elif 16 <= utc_hour or utc_hour < 3:
        return "Pacific"
    elif 18 <= utc_hour or utc_hour < 5:
        return "Hawaii"
    else:
        return None  # No active call window
```

---

## 📊 Expected Volume (Per Day)

| Metric | Target |
|--------|--------|
| Prospects Found | 200-500/day |
| Emails Sent | 100-300/day |
| SMS Sent | 100-300/day |
| Calls Made | 50-100/day |

---

## 🚨 Failure Handling

1. **Apollo Rate Limit**: Back off 5 minutes, then resume
2. **Vapi Call Failure**: Log and skip to next lead
3. **GHL Webhook Failure**: Retry 3x with exponential backoff
4. **Zero Leads**: Alert owner immediately

---

## Integration with Railway Worker

The `railway/app.py` scheduler must implement:

```python
# AGGRESSIVE AUTONOMOUS schedule
schedule.every(3).minutes.do(run_caller)      # 20 calls/hr (business hours)
schedule.every(3).minutes.do(run_outreach)    # 24/7 emails
schedule.every(10).minutes.do(run_prospector) # 24/7 prospecting
schedule.every(6).hours.do(send_status_report)
```

With timezone-aware lead selection for calls.

---

## 🤖 AUTONOMOUS CLOUD OPERATIONS

> [!CAUTION]
> The system MUST operate fully autonomously in the cloud without human intervention.

### Self-Healing Requirements

1. **safe_run() Wrapper**: ALL scheduled tasks wrapped in error handlers
   - Catches ALL exceptions
   - Logs error but NEVER crashes
   - Continues to next iteration

2. **Auto-Restart Mechanism**:
   - `/health` endpoint monitors scheduler heartbeat
   - If heartbeat > 5 minutes stale, auto-restart scheduler thread
   - Track restart count in `/stats`

3. **Fallback Strategies**:
   - If Supabase fails → Log and continue
   - If GHL fails → Retry 3x with backoff
   - If Vapi fails → Mark lead as "call_failed", move to next
   - If no leads → Pull from GHL contacts directly

### Research-First Protocol

Before making ANY external API call to a new service:

1. **Search official documentation** first
2. **Verify endpoint and auth method** from 2 sources
3. **Log findings** in operational_memory.md
4. **Test locally** before deploying

### Error Recovery Steps (Automated)

```
1. ERROR occurs in any function
2. safe_run() catches and logs: "[FUNC] ❌ ERROR (auto-recovered): {msg}"
3. Scheduler continues immediately
4. Error count tracked in stats
5. If error_count > 10 in 1 hour → Send alert to owner
```

### Cloud Autonomy Checklist

- [x] Runs on Railway (always-on)
- [x] Auto-restarts on crash (Railway restart policy)
- [x] Scheduler thread auto-recovery (/health endpoint)
- [x] All functions wrapped in safe_run()
- [x] No human intervention required for normal operation
- [x] Self-healing on transient API failures
- [x] Fallback to GHL contacts when Supabase empty

---

## 📧 Owner Notification

All outbound emails are BCC'd to owner for verification:

- `OWNER_EMAIL = "nearmiss1193@gmail.com"`
- Subject: `📧 SENT: {company} ({email})`
