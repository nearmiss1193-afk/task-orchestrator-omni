# SOP: INTER-AGENT COORDINATION PROTOCOL

## Context

Multiple AI agents operate within this codebase simultaneously. To prevent state-drift, cron-collisions, and file-clobbering, this protocol is **MANDATORY.**

## 1. The Startup Sync (The "Read" Phase)

Before taking any action, every agent MUST:

1. View `SOVEREIGN_MANIFEST.md` to see active deployments and playground boundaries.
2. Read the latest entries in the `🧬 INTER-AGENT COMMUNICATION LOG`.
3. Adhere to the **24/7 Cloud Mandate** in [sovereign_governance.md](file:///c:/Users/nearm/.gemini/antigravity/playground/empire-unified/directives/sovereign_governance.md).

## 2. Zero-Interference Production Rule

* **UNTOUCHABLES**: Any script ending in `_poller.py` or apps named `empire-distributor-v1` are PRODUCTION. DO NOT EDIT.
* **SHADOW SYSTEM**: All v2.0 development MUST stay within `execution/v2/` and use the `v2-` prefix for all cloud deployments.
* **UPTIME**: v1.x campaigns must have 100% uptime during the v2.0 build.

## 3. Modal Cron Governance

* **Limit**: We operate on a standard Modal plan. Cron slots are precious.
* **Rule**: Do not create new scheduled functions if they can be consolidated into the `v2-master-trigger` (Supabase Edge Function + Modal Webhook).

## 4. The Handover (The "Write" Phase)

Before ending a session or requesting user review:

1. Log a concise summary of work done and "where the ball is" in `SOVEREIGN_MANIFEST.md > 🧬 INTER-AGENT COMMUNICATION LOG`.
2. Cite any new files or infrastructure deployed.

---
**PENALTY FOR BREACH:** System instability and redundant credit consumption.
