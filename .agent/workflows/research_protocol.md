---
description: Mandatory research protocol when knowledge is unclear or failing
---

# Research Protocol

> [!CAUTION]
> **MANDATORY TRIGGER:** This protocol MUST be executed when ANY of these conditions are met:
>
> 1. You don't have clear knowledge about a technology/API/platform
> 2. Your existing approach fails (error codes, unexpected behavior)
> 3. You're using a new tool, API, or service for the first time
> 4. A command or API call returns an error you don't immediately understand

---

## ⛔ HARD RULE: Two-Source Verification

Before implementing ANY solution involving external services or APIs:

- [ ] **Source 1**: Search web for official documentation
- [ ] **Source 2**: Find a second source (tutorial, Stack Overflow, GitHub issue)
- [ ] **Cross-Reference**: Confirm both sources agree on the approach
- [ ] **Document**: Log findings in `operational_memory.md`

If sources conflict, **ask the user** before proceeding.

---

## Research Process

### Step 1: Identify the Gap

```
[RESEARCH TRIGGER] 
Reason: [unclear knowledge / error encountered / new technology]
Topic: [what needs to be researched]
```

### Step 2: Search (Minimum 2 Queries)

// turbo

```
search_web("official [technology] documentation [specific topic]")
search_web("[technology] [error message or task] tutorial")
```

### Step 3: Read & Extract

For each result:

1. Use `read_url_content` to get the actual content
2. Extract: requirements, auth methods, correct endpoints, env vars
3. Note any version-specific details

### Step 4: Verify Cross-Reference

Create a verification table:

| Aspect | Source 1 | Source 2 | Match? |
|--------|----------|----------|--------|
| Auth Method | | | ✅/❌ |
| Endpoint URL | | | ✅/❌ |
| Required Params | | | ✅/❌ |

### Step 5: Document in Brain

Add findings to `operational_memory.md`:

```markdown
## [Technology] - Verified [DATE]

**Sources:**
- [URL 1]
- [URL 2]

**Key Findings:**
- Auth: [method]
- Endpoint: [URL]
- Required: [params/env vars]
```

### Step 6: Implement with Confidence

Only after Steps 1-5 are complete, proceed with implementation.

---

## Failure Recovery

If your implementation fails AFTER research:

1. **Re-research** with the specific error message
2. Search: `"[exact error message]" [technology]`
3. Check GitHub Issues for the project
4. If still stuck after 2 research attempts → **Ask User**

---

## Example: Railway Deployment (What Should Have Happened)

**Trigger:** First time using Railway CLI

**Research:**

1. `search_web("Railway CLI deployment official documentation")`
2. `search_web("Railway environment variables how to set")`

**Findings:**

- Source 1: Railway Docs - needs `railway login`, then `railway up`
- Source 2: Tutorial - env vars set via dashboard or `railway variables set`

**Cross-Reference:** ✅ Both confirm dashboard or CLI for env vars

**Action:** Follow verified process

---

## Integration with Save Protocol

This protocol is referenced in `/save_protocol` under "Deep Research Before New Technology".

When triggered, announce:

```
[RESEARCH MODE] Initiating two-source verification for [topic]...
```
