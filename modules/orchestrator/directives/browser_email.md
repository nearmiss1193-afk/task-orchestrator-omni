# Directive: Browser-Based Email/Contact Search

## Goal

Locate a contact in GHL and verify their existence/status via browser automation (used when API access is restricted or for visual verification).

## Layer 2 Orchestration

- Routes search queries to the GHL Contacts smart list.

## Process

1. **Navigate**: Go to the Smart List contacts page.
2. **Search**: Enter the recipient's email or name into the search bar.
3. **Verify**: Wait for results to propagate.

## Edge Cases

- **No Search Bar**: If the input isn't found, try secondary selectors (`#contact-search`, `.location-contacts-list-search input`).
- **No Results**: Log as a search failure rather than a system error.

## Learnings

- The contact search bar sometimes takes 2-3 seconds to become interactive even after `domcontentloaded`.
- Force-pressing 'Enter' after typing is more reliable than clicking a search icon.
