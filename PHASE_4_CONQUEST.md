# PHASE 4: CONQUEST (SCALING THE EMPIRE)

Now that the "Sovereign Stack" is stable (Missions 1-30 Complete), we shift from **Construction** to **Expansion**.

## 🚀 STRATEGIC OBJECTIVES

### 1. THE SAW (Cold Email Artillery)

- **Current**: We rely on Inbound (GHL) and Organic Social (Siege).
- **Next Step**: Integrate a High-Volume Cold Emailer.
- **Tech**: Resend.com or Instantly.ai API.
- **Goal**: Send 500/day cold emails to "Predator" scraped leads.
- **File**: `modules/expanse/cold_email.py`.

### 2. THE VOICE NEXUS (Vapi 2.0)

- **Current**: 'Riley' answers calls.
- **Next Step**: Outbound Dialing Trigger.
- **Logic**: If a lead fills a form but doesn't book -> Riley calls them immediately ("Speed to Lead").
- **Integration**: Vapi Outbound API.

### 3. THE TREASURY (Stripe Integration)

- **Current**: Leads are marked "Won".
- **Next Step**: Auto-Charge.
- **Logic**: When GHL tag = "Closed", generate Stripe Invoice and SMS it to client.

## 🛠 IMMEDIATE ACTIONS

1. **Review**: Read `SOVEREIGN_MANUAL.md` to master current ops.
2. **Monitor**: Let `social_posting_loop` run for 24 hours. Check `brain_logs` tomorrow.
3. **Decide**: Choose ONE of the above objectives to start next.
