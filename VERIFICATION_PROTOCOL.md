# VERIFICATION PROTOCOL (DUE: 24 HOURS)

Before expanding to Phase 4, you must confirm Phase 3 yielded results.

## 1. CHECK RICHARD (MANDATORY)

* **Action**: Run `python check_brain.py` before doing ANYTHING else.
* **Verify**: Ensure the process is listed and active.

## 2. CHECK SOCIAL SIEGE

* [ ] **GHL Social Planner**: Log into GoHighLevel. Are there new Drafts/Posts scheduled?
* [ ] **Brain Logs**: In Dashboard Chat, type `Status`. Does it show "Social Content Generated" in the logs?

## 2. CHECK GOVERNOR

* [ ] **Uptime**: warning logs in `brain_logs`?
* [ ] **Silence**: Did the Governor trigger an "ALERT"? (Check email/SMS if you set that up).

## 3. CHECK LEADS

* [ ] **Supabase**: Run `Status` in chat. Did the lead count increase?

> **IF GREEN**: Proceed to Cold Email (Phase 4).
> **IF RED**: Run `modal app logs ghl-omni-automation` to debug.
