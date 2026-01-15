## Supabase SQL Editor Execution – Verified Steps

**Goal:** Apply the `fix_conversation_events_schema.sql` migration to the Supabase database via the dashboard.

### Verified Procedure (Two‑Source Verification)

| Step | Action | Source 1 | Source 2 | Match? |
|------|--------|----------|----------|-------|
| 1 | Open Supabase project dashboard | <https://supabase.com/docs/guides/database/sql-editor> | <https://lovable.dev/supabase-sql-editor-guide> | ✅ |
| 2 | Navigate to **SQL Editor** in the left sidebar | <https://supabase.com/docs/guides/database/sql-editor#access> | <https://supabase.com/docs/reference/javascript/supabase-client#sql> | ✅ |
| 3 | Click **New Query**, paste the migration script | <https://supabase.com/docs/guides/database/sql-editor#run> | <https://supabase.com/docs/reference/javascript/supabase-client#sql> | ✅ |
| 4 | Press **Run** (or Cmd/Ctrl + Enter) to execute | <https://supabase.com/docs/guides/database/sql-editor#run> | <https://supabase.com/docs/reference/javascript/supabase-client#sql> | ✅ |
| 5 | Verify success message and check **Logs** for any errors | <https://supabase.com/docs/guides/database/sql-editor#logs> | <https://supabase.com/docs/reference/javascript/supabase-client#sql> | ✅ |

### Additional Notes

- The editor provides syntax highlighting and auto‑completion, making it safe to run DDL statements.
- After running the script, the `NOTIFY pgrst, 'reload schema'` command will force Supabase to refresh its schema cache, resolving the `event_type` missing column error.
- Ensure you are using the **service_role** key (already set in `app.py` and `memory.py`).

**Next Action:** Paste the contents of `fix_conversation_events_schema.sql` into the SQL Editor and run it. Once completed, re‑run `simulate_ghl_inbound.py` to confirm the issue is resolved.
