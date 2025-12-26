# Directive: Lead Enrichment Dossier

## Goal

Automatically enrich new leads with deep-research data to facilitate high-context sales outreach.

## Layer 2 Orchestration (marketing-agent.ts)

- Triggers on new rows in Supabase `leads` table.
- Maps enrichment results to the `agent_research` JSONB column.

## Layer 3 Execution (ghl-browser.ts & ux_audit.py)

1. **Search**: Find the lead's LinkedIn profile and recent Google News mentions.
2. **UX Analysis**: Scan the lead's website for "revenue leaks" (e.g., missing lead magnets, slow load times, broken forms).
3. **Scoring**: Assign a 'Vibe Score' (1-100) based on brand consistency and market fit.

## Logic Flow

- If Vibe Score > 80: Set `status` = 'high_priority'.
- Generate a Markdown 'Site Audit' artifact.

## Learnings

- Use Google News search for company names rather than individuals for better "biz detail" extraction.
- UX leaks identified: No SSL, no CTAs above the fold, missing pixel tracking.
