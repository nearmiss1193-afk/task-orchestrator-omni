---
description: Save protocol - commit all session learnings to knowledge base and git
---

# Save Protocol

// turbo-all

When the user runs `/save_protocol`, execute the following steps:

## Steps

1. **Update Knowledge Base Files** — Review the current session and update:
   - `knowledge_base/operational_memory.md` — Add new section with session date, incidents found, fixes applied, and new sovereign laws learned
   - `knowledge_base/error_fixes.md` — Add new entries for any errors encountered (format: Error Type, Symptoms, Root Cause, Fix, Prevention)
   - `knowledge_base/system_recovery.md` — Add new recovery scenarios if applicable
   - Bump the version number in operational_memory.md

2. **Git Add & Commit** — Stage and commit all knowledge base changes:

   ```
   git add knowledge_base/
   git commit -m "SAVE PROTOCOL: [date] session learnings - [brief summary]"
   ```

3. **Confirm Save** — Report what was updated and the git commit hash

## Format for operational_memory.md entries

```markdown
### Section [N]: [Date] — [Title]
- **Incident:** [what happened]
- **Root Cause:** [why]
- **Fix Applied:** [what was done]
- **Sovereign Law:** "[lesson learned]"
- **Diagnostic Scripts:** [any scripts created]
```
