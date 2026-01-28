# AI Learning Log v1

## 2026-01-23: Case-Sensitive Query Bug

| Field | Value |
|-------|-------|
| **Issue** | 170 leads stuck at "new", 88% pipeline blocked |
| **Root Cause** | .eq("status", "new") is case-sensitive, missed "NEW" |
| **Solution** | Changed to .ilike("status", "new") for case-insensitive |
| **Time to Diagnose** | 10 minutes |
| **Implementation Time** | 2 minutes |
| **Dan's Feedback** | ✅ Deployed successfully |
| **Result** | All 170 leads now processable |
| **Confidence** | High (standard SQL pattern) |
| **Prevention** | Always use .ilike() for text matching in Supabase |
