# 🔧 System Recovery Guide

## MISSION CONTROL ACCESS

### Dashboard URL (24/7 Access)

**<https://client-portal-one-phi.vercel.app>**

Access from any device, anywhere in the world.

---

## 🚨 CRASH RECOVERY PROCEDURES

### Scenario 1: Local Computer Crashed

**Impact:** Local scripts stop, but cloud services continue

**What Keeps Running:**

- ✅ Vapi webhooks (Modal)
- ✅ Dashboard (Vercel)
- ✅ Database (Supabase)
- ✅ Email tracking (Resend)

**What Stops:**

- ❌ Local terminal processes
- ❌ Manual campaign triggers
- ❌ Local file access

**Recovery Steps:**

1. Restart computer
2. Open terminal in `c:\Users\nearm\.gemini\antigravity\scratch\empire-unified`
3. Run: `python run_save_protocol.py` to check system state
4. Run: `python cloud_inspector.py` to verify all endpoints

### Scenario 2: Modal Service Down

**Impact:** Webhooks stop responding

**Symptoms:**

- Vapi calls not being tracked
- Rescue Bridge not firing

**Recovery Steps:**

1. Check Modal dashboard: <https://modal.com/apps>
2. Run: `python -m modal deploy modal_webhooks_only.py`
3. Verify: `curl https://nearmiss1193-afk--health-live.modal.run`
4. Update Vapi webhook URL if needed

### Scenario 3: Supabase Issues

**Impact:** No data persistence

**Recovery Steps:**

1. Check Supabase status: <https://status.supabase.com>
2. Verify connection: `python check_logs.py`
3. Re-run schema if needed: `python apply_schema.py`

### Scenario 4: Vercel Dashboard Down

**Impact:** No web dashboard access

**Recovery Steps:**

1. Check Vercel status: <https://www.vercel-status.com>
2. Redeploy: `cd apps/client-portal && npx vercel --prod --yes`

### Scenario 5: Complete System Recovery

**Full restart procedure:**

```bash
cd c:\Users\nearm\.gemini\antigravity\scratch\empire-unified

# 1. Verify environment
python check_env.py

# 2. Check database
python check_logs.py

# 3. Deploy webhooks
python -m modal deploy modal_webhooks_only.py

# 4. Run system check
python cloud_inspector.py

# 5. Verify Vapi
python update_vapi_webhook.py

# 6. Run save protocol
python run_save_protocol.py
python send_save_protocol.py
```

---

## 📂 KEY FILE LOCATIONS

| File | Purpose |
| :--- | :--- |
| `.env` | All API keys and secrets |
| `modal_webhooks_only.py` | Persistent webhook deployment |
| `cloud_inspector.py` | Health check all systems |
| `gmail_credentials.json` | Gmail OAuth |
| `gmail_token.json` | Gmail access token |
| `knowledge_base/` | All AI brain knowledge |

---

## 🔑 CRITICAL CREDENTIALS (In .env)

- `SUPABASE_URL` - Database connection
- `SUPABASE_SERVICE_ROLE_KEY` - Database admin access
- `VAPI_PRIVATE_KEY` - Voice AI
- `GHL_API_KEY` - GoHighLevel
- `RESEND_API_KEY` - Email service
- `GMAIL_CLIENT_ID` - Email reading
- `GMAIL_CLIENT_SECRET` - Email access

---

## 📞 EMERGENCY CONTACTS

| Service | URL |
| :--- | :--- |
| Modal Status | <https://status.modal.com> |
| Supabase Status | <https://status.supabase.com> |
| Vercel Status | <https://www.vercel-status.com> |
| Vapi Status | <https://status.vapi.ai> |
| GHL Status | <https://status.gohighlevel.com> |

---

## 💾 BACKUP CHECKLIST

### Daily Automatic

- ✅ Supabase automatic backups
- ✅ Git commits pushed to GitHub

### Weekly Manual

- [ ] Export Supabase data
- [ ] Backup .env file securely
- [ ] Backup gmail_token.json
- [ ] Run full cloud_inspector.py
- [ ] Review system_logs for errors

---

**When in doubt:** Run `python cloud_inspector.py` first. It will tell you what's working and what's not.
