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

| Task | Interval | Description |
|------|----------|-------------|
| Prospecting | Every 15 min | Find new companies via Apollo |
| Email/SMS | Every 10 min | Process new leads queue |
| Calling | Every 5 min | Call next lead in timezone window |
| Status Report | Every 6 hours | Send stats to owner |

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
# Aggressive schedule
schedule.every(15).minutes.do(run_prospector)
schedule.every(10).minutes.do(run_outreach)
schedule.every(5).minutes.do(run_caller)
schedule.every(6).hours.do(send_status_report)
```

With timezone-aware lead selection for calls.
