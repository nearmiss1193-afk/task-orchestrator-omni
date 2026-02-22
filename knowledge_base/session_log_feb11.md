# Session Learnings — Feb 11, 2026

## What Happened

Full system resurrection and income-priority hardening in one session:

1. **Prospecting Pipeline** — Fixed 3 bugs preventing lead generation (wrong API key, wrong column names, missing ghl_contact_id)
2. **Self-Healing Heartbeat** — Added 3 crash-safe checks to system_heartbeat (outreach stall, lead pool empty, prospector stall)
3. **Lead Pool Exhaustion Crisis** — Diagnosed and fixed: 388 leads stuck at `outreach_sent` with NULL `last_contacted_at`
4. **Auto-Recycler Built** — New recycler runs before every outreach cycle (50 stale leads/cycle, 3-day cooldown)
5. **AI Audit PDF Pipeline** — Verified ALREADY LIVE and sending personalized audit PDFs with FDBR hooks

## What We Learned

| # | Lesson | Sovereign Law |
|---|--------|---------------|
| 1 | NULL `last_contacted_at` = lead permanently stuck | "Always set last_contacted_at when changing to outreach_sent" |
| 2 | Lead recycling was planned but never built | "Lead recycling must be automatic, not manual" |
| 3 | Self-healing checks must be independently try/excepted | "Self-healing cannot crash the parent function" |
| 4 | `ghl_contact_id` is NOT NULL — every insert needs it | "Use `prospector-{uuid}` for scraped leads" |
| 5 | The audit pipeline was already built but never verified working in prod | "Verify before building — check what exists first" |
| 6 | PageSpeed API returns 429 under load | "Pipeline must degrade gracefully when APIs fail" |

## Action Taken

- Recycled 336 leads back to `new` → pool went from 1 to 298
- Deployed auto-recycler to `auto_outreach_loop` in deploy.py
- Deployed self-healing heartbeat to Modal
- Verified audit emails sending in production (04:00-04:10 UTC)
- Prospector ran: +52 fresh leads (total 692)

## Future Prevention

- Auto-recycler prevents pool exhaustion (runs every 5 min)
- Self-healing heartbeat detects stalls within 30 min
- NULL `last_contacted_at` auto-fixed by recycler (50/cycle)
- All new checks are crash-safe (independent try/except)

***

# Session Learnings — Feb 22, 2026 (Phase 10: Human-in-the-Loop Architecture)

## What Happened

Replaced the conceptual "Hard Killswitch" with a precision-engineered **Sovereign Override Matrix** and **Anti-Hallucination Queue** on the Vercel Command Center Dashboard.

1. **Anti-Hallucination Queue Installed:** Built the `VerificationQueue` React component. It instantly polls Neon for pending Ayrshare drafts (`social_drafts`) and unverified inbound replies (`contacts_master`).
2. **Global Override Commlink Built:** Built the `OverrideConsole` chat module and the `/api/c2-override` Next.js Edge route.
3. **Zero-Trust PIN Auth:** The Override Edge API strictly demands the `1175` PIN prefix to authenticate execution payloads.
4. **React Client Fatal Exception Fixed:** Patched a severe React crash across `/inbox` and `/campaigns` caused by leftover Python API syntax (`supabase.table()` converted correctly to `.from()`).

## What We Learned

| # | Lesson | Sovereign Law |
| - | ------ | ------------- |
| 1 | AI Hallucinations require physical interception before execution | "Never automate calendar booking without human sentiment verification" |
| 2 | Hard shut-offs damage pipeline integrity | "Graceful component overrides > total system termination" |
| 3 | Python Supabase syntax (`.table`) is fatal inside Next.js Hooks | "Strictly audit JS SDK `.from()` methodology on the Edge" |

## Action Taken

- Deployed the `VerificationQueue` checklist to `page.tsx`.
- Deployed the `OverrideConsole` terminal to `page.tsx`.
- Pushed Edge API `/api/c2-override` to Vercel production to process the `1175` PIN.
- Purged legacy Python Database calls from `campaigns` and `inbox` React schemas.
- Triggered Vercel `--prod --force` deployment to bake in the Phase 10 matrices.
