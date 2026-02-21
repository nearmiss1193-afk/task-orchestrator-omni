# Sovereign Secret Protocol (SSP)

## OVERVIEW

The Sovereign Secret Protocol is a mandatory security framework designed to prevent the exposure of sensitive API keys and credentials. It mandates a "Zero Hardcode" policy across the entire Sarah AI ecosystem.

## THE "ZERO HARDCODE" POLICY

1. **NO CREDENTIALS IN CODE**: API keys, database passwords, and secrets must NEVER be hardcoded in `.py`, `.html`, `.js`, or `.md` files.
2. **ENVIRONMENT VARIABLES ONLY**: All secrets must be accessed via `os.getenv()` in Python or injected during deployment for front-end assets.
3. **MODAL SECRETS**: All cloud deployments must use the `modal.Secret` system via the `VAULT` constant.

## SECURE DASHBOARD AUTHENTICATION

The Sovereign Dashboard is protected by a dual-layer authentication system:

- **Front-end Gate**: Controlled by `SESSION_CODE` (`empire_2026`).
- **Back-end Validation**: The `sovereign_stats` endpoint requires a mandatory `X-Dashboard-Code` header, validated against the `DASHBOARD_ACCESS_CODE` stored in Modal secrets.

## PRE-COMMIT CHECKLIST

Before pushing any code, developers (and agents) must verify:

- [ ] No strings starting with `AIzaSy` (Google API keys) exist in the codebase.
- [ ] No `.env` files or dump files (e.g., `env_dump.txt`) are tracked.
- [ ] All new secrets are added to the Modal `VAULT` and the local `.env.example`.

## INCIDENT RESPONSE

If a leak is detected:

1. **IMMEDIATE ROTATION**: Revoke the leaked key in the provider's dashboard (Google, OpenAI, etc.).
2. **SECRET PURGE**: Use `git filter-repo` or similar tools to remove the secret from history if it was pushed.
3. **UPDATE VAULT**: Update the Modal secret with the new key immediately.
