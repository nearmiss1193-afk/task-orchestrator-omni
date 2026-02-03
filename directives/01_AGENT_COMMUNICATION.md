# DIRECTIVE: AGENT COMMUNICATION PROTOCOL

**PRIORITY:** CRITICAL - MANDATORY
**SCOPE:** ALL AGENTS (Human, AI, Modal, Local)

## PURPOSE

To ensure a persistent, shared memory state across all agents co-working on the Empire Unified System. This prevents collision, redundancy, and loss of context between sessions.

## 1. THE BROADCAST RULE

**Rule:** Every task MUST begin and end with a broadcast event.

### A. Start of Task (The "Look-Ahead")

Before executing any tools, the agent must run:

```bash
python scripts/broadcast_event.py "TASK START: [Objective] - [Key Steps]" "TASK_INIT"
```

*Purpose:* Alerts other agents that this domain is active/locked.

### B. End of Task (The "Handoff")

Upon completion or pause, the agent must run:

```bash
python scripts/broadcast_event.py "TASK COMPLETE: [Outcome] - [Next Steps]" "TASK_DONE"
```

*Purpose:* Logs the final state so the next agent doesn't re-do work.

## 2. THE INVESTIGATION RULE

**Rule:** Before answering a user question about system state, the agent must:

1. Check `orchestrator_logs.txt` (or Supabase `brain_logs`).
2. Read the latest `system_status_report.md`.
3. Check `task.md` for active items.

## 3. LOGGING STANDARDS

- **Format:** `[TIMESTAMP] [LEVEL] MESSAGE`
- **Levels:**
  - `TASK_INIT`: Starting a major unit of work.
  - `TASK_DONE`: Work unit complete.
  - `CRITICAL`: System failure or blocker.
  - `INFO`: General progress.

## 4. FAILURE PROTOCOL

If `broadcast_event.py` fails (e.g., Supabase offline):

1. **Fallback:** Write manual entry to `orchestrator_logs.txt`.
2. **Alert:** Notify user in the final report.

---
*Signed: Orchestrator Sovereign Executive*
