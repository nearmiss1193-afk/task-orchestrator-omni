# Directive: GHL Funnel Creation

## Goal

Autonomous creation of a high-converting funnel inside GoHighLevel using browser automation.

## Inputs

- `name`: Name of the funnel to create.
- `businessType`: Context for the funnel content (optional).

## Layer 3 Execution Tools

- `ghl-browser.ts`: Orchestrates the browser session.
- `execution/ghl_create_funnel.py`: (Planned) Logic for DOM interactions.

## Process

1. **Navigate**: Go to the Funnels/Sites section.
2. **Check Existence**: Search for an existing funnel with the same name to avoid duplicates.
3. **Select Method**: Choose "New Funnel" -> "From Scratch".
4. **Input Data**: Enter the funnel name and submit.
5. **Add Landing Page**: Create the first step titled "Landing Page".

## Edge Cases

- **Existing Funnel**: If found, enter it instead of creating a new one.
- **Blocking Modals**: Use the "Search & Destroy" modal clearing logic if a modal obscures the "New Funnel" button.
- **Selector Timeout**: If Sites sidebar is missing, force-navigate to `/v2/location/{id}/funnels/funnel`.

## Learnings

- GHL uses heavy SPAs; `networkidle2` is often too slow, use fixed timeouts + robust existence checks.
- `:contains` pseudo-selector is invalid in modern CSS; use `page.evaluate` with `textContent.includes()`.
- Session persistence via `userDataDir` is critical to avoid 2FA loops.
