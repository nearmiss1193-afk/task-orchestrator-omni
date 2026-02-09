# Working Commands Log

> **Purpose:** Track successful methods during sessions to prevent forgetting working solutions.
>
> **Update this file IMMEDIATELY after any successful operation.**

---

## Feb 5, 2026 - Email Sending

| Method | Command/Syntax | Status | Notes |
|--------|----------------|--------|-------|
| `reliable_email.py` | `python reliable_email.py` | ✅ SUCCESS | Gmail API configured, works 100% |
| V3 Email Packages | `python generate_v3_packages.py` | ✅ SUCCESS | PageSpeed screenshots, traffic lights |
| Gmail API Sender | `gmail_api_sender.send_email()` | ✅ SUCCESS | Requires credentials.json |

---

## Feb 5, 2026 - Modal Deployment

| Method | Command/Syntax | Status | Notes |
|--------|----------------|--------|-------|
| Modal Deploy | `python -m modal deploy deploy.py` | ✅ SUCCESS | Use `-m modal` on Windows |
| Track Email Open endpoint | `HTTP 200` | ✅ SUCCESS | Logs to Supabase email_opens |

---

## Feb 5, 2026 - Board Protocol

| Method | Command/Syntax | Status | Notes |
|--------|----------------|--------|-------|
| Board Query | `python scripts/board_call_raw.py "QUESTION"` | ✅ SUCCESS | All 4 AIs respond |
| Results Location | `board_call_raw.json` | ✅ SUCCESS | JSON array of responses |

---

## Template for Future Entries

```markdown
## [Date] - [Task Category]

| Method | Command/Syntax | Status | Notes |
|--------|----------------|--------|-------|
| [Tool Name] | [Exact Command] | ✅ SUCCESS / ❌ FAILED | [Important Details] |
```

---

## Quick Reference: Priority 1 Methods (TRY FIRST)

| Task | Priority 1 Method | File Location |
|------|-------------------|---------------|
| Email Sending | `reliable_email.py` | `./reliable_email.py` |
| Email Verification | Hunter.io API | Via Modal endpoint |
| Prospecting | Modal cloud functions | `./deploy.py` |
| Board Decisions | `board_call_raw.py` | `./scripts/board_call_raw.py` |
| File Editing | Multi-replace tool | Cursor/Antigravity native |
