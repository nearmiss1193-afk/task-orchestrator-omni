# Capabilities & Gaps — Feb 11, 2026

## Active Capabilities ✅

| Capability | Status | Location |
|-----------|--------|----------|
| Autonomous Outreach (email) | ✅ LIVE | `auto_outreach_loop` every 5 min |
| AI Audit PDF Generation | ✅ LIVE | `audit_generator.py` + `dispatch_audit_email` |
| FDBR Privacy Hook | ✅ LIVE | Always-red finding for FL businesses |
| A/B Subject Line Testing | ✅ LIVE | 4 variants tracked in `outbound_touches` |
| Lead Prospecting (Google Places) | ✅ LIVE | `auto_prospecting` via heartbeat trigger |
| Lead Auto-Recycling | ✅ LIVE | 50/cycle, 3-day cooldown, crash-safe |
| Self-Healing Heartbeat | ✅ LIVE | Outreach stall, pool empty, prospector stall |
| Email Open Tracking | ✅ LIVE | Tracking pixel via Resend |
| SMS via GHL Webhook | ✅ LIVE | Business hours only (Mon-Sat 8-6) |
| Voice Calls via Vapi | ✅ LIVE | Business hours only |
| System Health Monitoring | ✅ LIVE | `system_health_log` every 5 min |
| System Check Script | ✅ READY | `scripts/system_check.py` |

## Known Gaps 🔴

| Gap | Impact | Priority | Fix |
|-----|--------|----------|-----|
| PageSpeed API 429s | Audit PDFs missing speed score | MEDIUM | Add API key or cache results |
| No external health watchdog | Missed downtime | MEDIUM | UptimeRobot on `/health_check` |
| No daily digest email | Dan can't see results at a glance | LOW | New cron (slot 3/4) |
| No reply tracking | Can't measure audit vs generic performance | MEDIUM | Resend webhook for replies |
| No Sunbiz prospecting | Missing 60-70% of Lakeland businesses | LOW | Future enhancement |
| Follow-up email timing | Hardcoded 3/7 day intervals | LOW | Make configurable |

## Cron Budget

| Used | Total | Remaining |
|------|-------|-----------|
| 2 | 4 | 2 slots |

**Active:** heartbeat (*/5), outreach (*/5)
**Manual:** prospecting, lead sync, self-learning
