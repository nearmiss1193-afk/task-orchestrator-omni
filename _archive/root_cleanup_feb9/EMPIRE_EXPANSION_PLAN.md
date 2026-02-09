# Empire Expansion: Phase 3 Strategy

## Goal

Transition from "Functional Autonomy" to **"Massive Scale"**.
We will stress-test the system, increase throughput by 10x, and activate the final media channel: **Voice**.

## Core Objectives

### 1. Volume Scaling (The "Floodgate")

- **Current**: 5 leads/batch (Safety Limit).
- **Target**: 50 leads/batch (Production Scale).
- **Mechanism**: Update `deploy.py` cron jobs and Supabase limits.
- **Risk**: GHL API Rate Limits (Need to implement queueing/backoff).

### 2. Voice Concierge (The "Closer")

- **Technology**: Vapi.ai + Bland AI (Fallback).
- **Integration**:
  - Inbound Call handling for Missed Calls (Backup to SMS).
  - Outbound "Courtesy Call" for warm leads (Nurture Day 3).
- **Action**: Deploy `vapi_bridge.py` logic to Modal.

### 3. Resilience (The "Shield")

- **Chaos Testing**: Deliberately inject bad data to test error handling.
- **Auto-Recovery**: If Agent crashes, the Governor detects and restarts it (Self-Healing).

## Implementation Roadmap

### Mission 22: High-Volume Lead Flow

- [ ] Increase `lead_research_loop` limit to 50.
- [ ] Implement `RateLimitGuardian` in `deploy.py`.
- [ ] Verify GHL "Conversations" view handles the load.

### Mission 23: Voice Layer Activation

- [ ] Configure `VAPI_API_KEY` in Modal Secrets.
- [ ] Create `modules/expanse/voice_concierge.py`.
- [ ] Connect Voice Webhook to `ghl-omni-automation`.

### Mission 24: The "Warlord" Dashboard

- [ ] Add "Revenue Projected" vs "Revenue Realized" metrics.
- [ ] Visual Map of Lead Sources (City/Niche).

## Mission 25: Dashboard Command (Deepening) [COMPLETE]

- [x] **Objective 1: Tactical Dossiers**: Deep Intel Modal.

### Objective 2: Live Scoring: Dynamic Evaluation Engine

- [x] **Objective 3: Direct Action**: Command Buttons wired to DB.

## Mission 26: Reality Protocol (The Great Purge) [COMPLETE]

- [x] **Action**: Wiped 1581 "Chaos Lead" records.
- [x] **Action**: Verify `deploy.py` Sync Logic with Real GHL (Identity/Location Verified).
- [x] **Goal**: Populate Dashboard with REAL leads only.

## Mission 27: The Voice Nexus (Vapi.ai) [COMPLETE]

- [x] **Objective**: "The Closer" Deployed.
- [x] **Inbound**: Logic ready for handling missed calls.
- [x] **Outbound**: Automate "Warm Lead Courtesy Calls" (Day 3).
- [x] **Autonomy**: Implemented Transient Assistant (No manual ID setup).
- [x] **Feature**: Live Call Logs in Dashboard (via Brain Logs).

## Mission 28: Social Siege (Omni-Presence) [COMPLETE]

- [x] **Objective**: Multi-Channel Response Logic.
- [x] **Action**: Updated Spartan to be Channel-Aware (IG/FB/SMS/Email).
- [x] **Goal**: 4-Channel Attack Vector Ready (Logic Layer).
- [x] **Status**: Deployed.

## Mission 29: The Governor (Self-Healing V2) [COMPLETE]

- [x] **Objective**: Automated Oversight.
- [x] **Logic**: Installed `GovernorAgent` (Hourly Monitor).
- [x] **Action**: Checks GHL/Supabase connectivity + Log Staleness.
- [x] **Alerting**: "Zombie Detect" logic active.

## Mission 30: Sovereign Handover [COMPLETE]

- [x] **Objective**: Golden Image.
- [x] **Action**: Deployment Finalized.
- [x] **Action**: Final Documentation (`Sovereign_Manual.md`).
- [x] **Status**: SYSTEM COMPLETION. (ODA PROTOCOL SUCCESS).

## Phase 4: The Sovereign App & Ecosystem (Next)

**Goal:** Provide the "Interface" for the customer to interact with our Agents.

### Mission 31: Client Portal App (The "Body")

- **Tech:** React / Next.js PWA.
- **Features:**
  - **Login:** Email/Phone (Auth0 or GHL OTP).
  - **Concierge Chat:** UI for `concierge_chat`.
  - **Marketplace:** One-click upgrades (Office Manager, etc.).

### Mission 32: Voice Tuning (The "Soul")

- **Action:** Calibrate Vapi.ai latency and voice selection.
- **Action:** Feed "Office Manager" specialized knowledge (Inventory types).

### Mission 33: Traffic Flood (The "Fuel")

- **Action:** Turn on Ads -> Funnel -> App.

## Phase 5: Vertical Domination (Completed)

**Goal:** Establish specialized beachheads in 10 high-value niche markets.

- [x] **1. HVAC:** "Cooling Cal" (Deployed)
- [x] **2. Plumbers:** "Dispatch Dan" (Deployed)
- [x] **3. Roofers:** "Estimator Eric" (Deployed)
- [x] **4. Electricians:** "Electrician Ellie" (Deployed)
- [x] **5. Solar:** "Sunny Sam" (Deployed)
- [x] **6. Landscaping:** "Green Thumb Gary" (Deployed)
- [x] **7. Pest Control:** "Exterminator Ed" (Deployed)
- [x] **8. Cleaning:** "Maid Mary" (Deployed)
- [x] **9. Restoration:** "Flood Phil" (Deployed)
- [x] **10. Auto Detail:** "Detail Dave" (Deployed)

**Status:** ALL 10 VERTICALS LIVE on `deploy.py` endpoints.
**Next:** Traffic Injection.
