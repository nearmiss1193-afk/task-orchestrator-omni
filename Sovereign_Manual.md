# SOVEREIGN OPERATIONS MANUAL (v1.0)
>
> **CLASSIFICATION**: COMMANDER EYES ONLY
> **SYSTEM**: EMPIRE UNIFIED (Modal + GHL + Supabase)

## 1. SYSTEM OVERVIEW

The "Empire Unified" system is a self-driving agency engine. It performs three core loops:

1. **Inbound/Outreach**: (Spartan) - Responds to leads via SMS/Email using Gemini.
2. **Social Siege**: (Siege) - Posts high-value content to LinkedIn/FB every 8 hours.
3. **Governance**: (Governor) - Self-heals and alerts you if the system goes silent.

## DIRECTIVE 0: OMNI-AGENCY (AUTONOMED SYSTEM)

**AUTHORITY:** The Sovereign Agent is granted full autonomous execution rights for all system repairs, process management, and code patches.
**CONSTRAINT:** Financial transactions (> $0.00) require explicit user approval.
**EXECUTION:** Identify -> Fix -> Verify -> Report. Do not ask for permission to repair.

## THE SOP (MANDATORY)

**Before & After Every Task:**

1. **CHECK RICHARD**: Run `python check_brain.py`. Ensure he is awake.
2. **UPDATE RICHARD**: Report your status to him.

---

---

## 2. COMMAND CENTER (Dashboard)

**URL**: `http://localhost:3000` (Local)
**Access**: Open `modules/orchestrator/dashboard` and run `npm run dev`.

### **Chat Commands (Oracle)**

Type these into the dashboard chat for instant intel:

- `Status`: Shows Verified Lead Count, DB Connectivity, and Governor Status.
- `Social`: Shows the current target niche and last posting time.
- `Leads`: Shows deep database stats.
- `How`: Explains the active code logic (`deploy.py`).

---

## 3. CORE MAINTENANCE (The "One Command")

All logic lives in `deploy.py`. To update, restart, or patch the *entire* business:

```bash
modal deploy deploy.py
```

*This command pushes your local code to the Modal cloud. It updates all active loops/cron jobs instantly.*

---

## 4. TROUBLESHOOTING

**Symptom**: "Dashboard chat says 'Warming Up' forever."
**Fix**: Your `GEMINI_API_KEY` might be rate-limited. The system is still running (Command Mode works), but AI 'brain' features are paused.
**Action**: Check Modal Secrets or wait 1 hour.

**Symptom**: "No Leads appearing."
**Fix**: Check GHL Webhook connection.
**Action**: Run `status` in chat. If 'System' is offline, run `modal deploy deploy.py` to reboot.

---

## 5. SCALING (Floodgate Protocol)

To increase lead volume:

1. Open `deploy.py`.
2. Find `outreach_scaling_loop`.
3. Change `limit(50)` to `limit(500)`.
4. Run `modal deploy deploy.py`.
*Warning: Ensure your GHL Email/SMS quotas can handle the volume.*

---

### END OF MANUAL
