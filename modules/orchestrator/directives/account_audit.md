# Directive: Account Audit

## Goal

Extract a comprehensive inventory of GHL assets (Funnels, Pipelines, Tags) for reporting and analysis.

## Layer 3 Execution Tools

- `ghl-browser.ts`: Orchestrates the browser session.

## Process

1. **Navigate**: Sequentially visit the following URLs (appends location ID from URL or Env):
   - `/v2/location/{id}/funnels/funnel`
   - `/v2/location/{id}/opportunities/pipelines`
   - `/v2/location/{id}/settings/tags`
2. **Extract**: Use DOM selectors to scrape names and statuses of assets.
3. **Aggregate**: Store results in a JSON object.

## Edge Cases

- **Missing Location ID**: If not found in URL or Env, skip specific scans and return an error flag.
- **Empty States**: If a table is empty, record "0 items found" rather than failing.

## Learnings

- Pipelines often load lazily; wait for `tbody tr` or `.hl-card`.
- Tags page is settings-specific; direct URL navigation is faster than clicking through "Settings" -> "Tags".
