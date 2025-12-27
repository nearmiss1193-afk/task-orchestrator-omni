# SOVEREIGN MANUAL (V1.0)

**System Architecture & Operations Guide**

## 1. System Overview

The **AI Service Co (Empire United)** is a fully autonomous, headless AI agent ecosystem deployed on **Modal Cloud**. It handles lead generation, research, outreach, and engagement across Email, SMS, Voice, and Social channels.

| Component | Technology | Function |
| :--- | :--- | :--- |
| **Brain** | Gemini 1.5 Pro | Decision Making, Email Drafting, Research. |
| **Compute** | Modal Cloud | Serverless execution of loops and webhooks. |
| **Database** | Supabase | `contacts_master`, `brain_logs`, `staged_replies`. |
| **CRM** | GoHighLevel (GHL) | Contact sourcing, SMS/Email delivery, UI. |
| **Voice** | Vapi.ai | Outbound calls using "Transient Assistant" architecture. |

---

## 2. Core Loops (Automated)

### A. The Research Engine (`research_lead_logic`)

- **Trigger**: New contact in GHL (Tag: `trigger-vortex`).
- **Action**: Scrapes website, generates "Tactical Dossier", scores lead (0-100).
- **Output**: Updates `contacts_master` with `raw_research`.

### B. The Spartan Responder (`ghl_webhook`)

- **Trigger**: Inbound message (SMS, Email, Instagram, FB).
- **Action**: Generates AI reply using Channel-Aware logic.
- **Turbo**: Auto-sends if confidence > 0.7. Else stages for approval.

### C. The Voice Nexus (`voice_concierge_loop`)

- **Schedule**: Every 4 Hours.
- **Logic**: Finds `nurtured` leads with Score > 90 who haven't booked.
- **Action**: Initiates Vapi call (Rachel Voice) to confirm interest.

### D. The Governor (`system_guardian`)

- **Schedule**: Every 1 Hour.
- **Logic**: Checks `brain_logs` for activity.
- **Alert**: If no activity > 60 mins ("Zombie Mode"), logs Critical Alert.

---

## 3. Deployment & Recovery

### Deploying Updates

```bash
python -m modal deploy deploy.py
```

### Manual Sync (Force GHL -> Supabase)

If the database desynchronizes:

```bash
python -m modal run deploy.py::manual_ghl_sync
```

### Logs & Monitoring

Visit the Modal Dashboard: `https://modal.com/apps/nearmiss1193-afk` / `logs`.

### Kill Switch

To stop all operations immediately:

1. Log into Modal Dashboard.
2. Click **Stop App** on `empire-dash`.

---

## 4. Troubleshooting

**Error: PGRST205 (Schema Cache)**

- **Symptom**: "Could not find table 'contacts_master'".
- **Fix**: The system uses a "Minimal Payload" strategy to bypass column mismatches. If this fails, user must log into Supabase Dashboard -> Settings -> API -> **Reload Schema Cache**.

**Error: 403 Forbidden (GHL)**

- **Symptom**: "Access to this location is forbidden".
- **Fix**: Ensure `GHL_LOCATION_ID` is updated in `.env` and `deploy.py`. The system currently hardcodes the verified LocationID.

---

**STATUS: OMNI-DIRECTIONAL AUTONOMY ACTIVE.**
*Authorized by: NEAR*
