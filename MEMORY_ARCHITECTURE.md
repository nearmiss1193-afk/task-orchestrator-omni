# 3-LAYER MEMORY ARCHITECTURE

## Overview

Memory access is controlled at 3 layers to prevent pollution, conflicts, and hallucinations.

---

## Layer 1: MEMORY MANAGER (Write Authority)

**The ONLY agent allowed to write to canonical memory tables.**

### Agent: `memory_manager`

**Writes to:**

- `contacts` (summary, stage, opt_out, sentiment)
- `memories` (validated facts with confidence scores)

**Does NOT write:**

- Freeform speculation or "vibes"
- Raw transcripts as "facts"
- Unvalidated suggestions

**System Prompt Addition:**

```
You are the Memory Manager. You are the ONLY agent authorized to write to long-term memory tables (contacts, memories).

Your responsibilities:
1. Validate memory suggestions from other agents
2. Resolve conflicting facts (keep highest confidence)
3. Never store: SSN, credit cards, health, religion, politics
4. Always include confidence scores (0.0-1.0)
5. Delete data when user requests opt-out

Before writing, verify:
- Is this a business-relevant fact?
- Is confidence >= 0.7?
- Does it conflict with existing memory?
```

---

## Layer 2: ORCHESTRATOR (Read + Routing)

**Reads memory, decides routing, passes context to specialists.**

### Agent: `orchestrator` / `sarah_dispatcher`

**Can:**

- READ from `contacts`, `memories`, `interactions`
- Decide which specialist runs
- Pass relevant context to specialists
- Trigger escalation

**Cannot:**

- Write to `contacts` or `memories`
- Change pricing, guarantees, policies

**System Prompt Addition:**

```
Memory permission:
- You may READ contact memory and recent interactions.
- You may NOT write to long-term memory tables (contacts/memories).
- If you discover a useful fact, output it under: "memory_suggestions" with confidence.
- Pass only relevant context to specialist agents.
```

---

## Layer 3: SPECIALISTS (Read-Only + Ephemeral Notes)

**Task-specific agents with read-only memory access.**

### Agents

- `spartan_responder` (SMS/Email responses)
- `social_siege` (Marketing posts)
- `outreach_scaler` (Bulk reactivation)
- `hiring_captain` (Job applicant filtering)
- `research_agent` (Intel/dossiers)
- `followup_generator` (Next-touch suggestions)

**Can:**

- READ from `contacts`, `memories`
- WRITE to `interactions` (logs)
- WRITE to `memory_suggestions` (proposals)
- WRITE to `playbook_updates` (improvement ideas)
- WRITE to `agent_notes` (ephemeral, auto-delete after 24h)

**Cannot:**

- Write to `contacts` or `memories` (canonical facts)

**System Prompt Addition:**

```
Memory permission:
- You may READ contact memory for personalization.
- You may NOT write to memory tables directly.
- If you discover facts, output under "memory_suggestions":
  {"key": "...", "value": "...", "confidence": 0.8}
- Your suggestions will be reviewed by the Memory Manager.
```

---

## NO Memory Access

**These agents should NOT access customer memory:**

- Code-writing agents
- Deployment agents
- File system agents
- Database migration agents

**Why:** Dangerous if they "learn" the wrong thing and act on it.

---

## Required Tables

| Table | Purpose | Who Writes |
|-------|---------|------------|
| `contacts` | Canonical profile | Memory Manager ONLY |
| `memories` | Validated facts | Memory Manager ONLY |
| `interactions` | Raw transcripts | All agents (logs) |
| `memory_suggestions` | Proposed facts | Specialists |
| `playbook_updates` | Script improvements | Specialists + Optimizer |
| `event_log` | Tool successes/failures | All agents |
| `agent_notes` | Ephemeral working notes | Specialists |

---

## Required Flow Per Inbound

```
1. Orchestrator: get_memory(phone)
2. Sarah/Responder: respond using injected memory
3. Memory Extractor: parse transcript → JSON suggestions
4. Memory Manager: validate → commit approved updates
5. (Optional) Optimizer: log failure modes for daily review
```

---

## Self-Learning Safe Zones

**Agents CAN self-improve:**

- Follow-up wording variants
- Objection responses
- KB gap additions
- Routing thresholds (confidence < 0.8 → escalate)

**Agents CANNOT self-edit (LOCKED CONSTANTS):**

- Pricing ($997, $1997, $4997)
- Guarantees (30-day, results, refund)
- Compliance rules (TCPA, CAN-SPAM)
- Escalation numbers ((863) 337-3705)
- Booking link (link.aiserviceco.com/discovery)

---

## Implementation Checklist

- [ ] Create `memory_suggestions` table
- [ ] Create `agent_notes` table (with 24h TTL)
- [ ] Update `sarah_dispatcher.py` with read-only permissions
- [ ] Create `memory_manager.py` with write authority
- [ ] Add permission blocks to all agent prompts
- [ ] Test flow: inbound → memory read → response → suggestions → manager writes
