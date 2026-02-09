# 🏛️ EMPIRE SOVEREIGNTY BLUEPRINT: V5.0

This document outlines the strategic roadmap for the "Empire Unified" to achieve total data sovereignty and 100% reliable AI memory.

## 1. Individual AI Perspectives

* **Claude (Executive)**: Focus on **Synchronization**. The failure was a race condition. We need distributed locking or serialized state updates to ensure Sarah sees the data before she speaks.
* **ChatGPT (Engineer)**: Focus on **Infrastructure**. Move context upstream. If Sarah is calling a lead, she should carry her memory with her (Metadata Injection) rather than looking for it in a database mid-call.
* **Gemini (Researcher)**: Focus on **Verification**. Root-cause the Vapi caching layer for Dan's specific number. Ensure the "Hard Refresh" actually clears the Vapi cloud state.
* **Grok (Strategist)**: Focus on **ROI**. Implement "Lead Scoring" in the sync engine. Don't waste Vapi credits or Sarah's time on leads with incomplete data dossiers.

---

## 2. Collective Consensus: The 3 Pillars

1. **Unified Lead Source of Truth**: Data fragmentation across GHL, Resend, and Supabase must end. We will build a single `master_lead_dossier` that serves as the "Brain" for all outreach.
2. **Pre-flight Metadata Injection**: We will no longer rely on the "Bridge" to fetch names. We will inject the Name and Context into the Vapi request *payload*. Sarah will know who you are before the call even connects.
3. **Success Pattern Feedback Loop**: We will link GHL "Won" tags back to Vapi "Transcripts". The system will automatically update Sarah's sales prompt based on what actually books appointments.

---

## 3. Steps to Success

### Step 1: Deploy the Unified Sync (Dashboard Core)

* Implement `workers/lead_unifier.py` as a Modal Cron.

* Target: Sync 100% of Resend open-rates and GHL pipeline stages into Supabase.

### Step 2: Transition to Metadata Injection (Vapi Stability)

* Implement `modules/vapi/metadata_injector.py`.

* Update the outreach worker to calculate the `metadata` object before calling the Vapi API.
* Verify: Sarah greets Dan by name in < 1 second.

### Step 3: SOP Purge & Tool Hierarchy

* Clean `operational_memory.md`.

* Establish **Resend** as the sovereign cold-email engine and **GHL** as the CRM/SMS bridge.
* Enforce the **4-Cron Limit** for system stability.

### Step 4: Enable the Learning Loop

* Schedule the `self_learning_cron` to perform daily transcript analysis.

* Update Sarah's `SALES_SARAH_PROMPT` with "Winning Patterns" found in high-converting calls.

---

## 🚀 Execution Order

1. **Approval** -> 2. **Metadata Draft** -> 3. **Sync Engine Draft** -> 4. **Unified Leaderboard Deployment**.
