---
description: Mandatory email verification and sending protocol for cold outreach
---
# Email Outreach Protocol Workflow

// turbo-all

## Purpose

Ensure all outbound emails have **verified email addresses** before sending. NEVER guess emails.

> [!CAUTION]
> **BEFORE SENDING ANY EMAIL:**
>
> 1. VERIFY the email address exists (no guessing info@, contact@, service@)
> 2. RESEARCH the contact name (no "Dear Team")
> 3. GET owner approval on draft content
> 4. ONLY THEN send
>
> **Guessing = Bounces = Wasted effort + damages sender reputation**

> [!IMPORTANT]
> **MANDATORY REQUIREMENTS CHECK (Added Feb 5, 2026)**
>
> Before proceeding to Step 6 (Send), verify ALL of these:
>
> - [ ] Street Light HTML styling with colored traffic lights (🔴🟡🟢)
> - [ ] PageSpeed screenshot attached (PageSpeed_{Domain}.png)
> - [ ] Audit PDF/link attached (Audit_{Domain}.pdf)
> - [ ] Open tracking pixel at bottom of email body
>
> **If ANY is missing → STOP → Cannot proceed until fixed**


## Complete Steps (MANDATORY)

### Step 1: Research Contact Information

For each prospect, run this verification sequence:

1. **Hunter.io API** - Search by domain
2. **Apollo.io API** - Search by company
3. **Company Website** - Check Contact/About/Team pages
4. **LinkedIn** - Find owner/manager
5. **Google Search** - "[Company Name] [City] FL owner email"
6. **Web Search** - Use `search_web` tool to find verified contact

**If ALL fail after 10 minutes:** Add to Manus batch list, skip for this batch.

### Step 2: Verify Email Format

```bash
# Use this command to verify email exists
python scripts/verify_email.py <email_address>
```

Or check MX records exist for domain:

```bash
nslookup -type=MX domain.com
```

### Step 3: Document Verified Emails

Create/update prospect list with:

- [ ] Company name
- [ ] Verified email (source noted)
- [ ] Contact name (if found)
- [ ] Research notes

### Step 4: Draft Email Content

- Use bfisher format with traffic light table
- Include PageSpeed data if available
- Attach PDF audit report
- Include CAN-SPAM footer

### Step 5: Get Owner Approval

Use `notify_user` to present:

1. Draft emails for review
2. List of verified email addresses
3. Attachments to be sent

**DO NOT SEND without approval.**

### Step 6: Send After Approval

Only send after Dan approves:

```bash
python scripts/send_batch1_live.py
```

### Step 7: Verify Delivery

Check for bounces within 30 minutes:

- Open Gmail sent folder
- Check for Mail Delivery Subsystem errors
- Report any bounces immediately

## Email Verification Tools

| Tool | Use For | API Key |
|------|---------|---------|
| Hunter.io | Domain search | In .secrets/secrets.env |
| Apollo.io | Company search | In .secrets/secrets.env |
| search_web | Manual research | Built-in tool |
| Gmail | Send + verify | gmail_token.json |

## NEVER DO

❌ Guess email formats (info@, contact@, service@)
❌ Send without verifying email exists
❌ Send without owner approval
❌ Use "Dear Team" without trying to find contact name
❌ Skip verification steps "to save time"

## ALWAYS DO

✅ Research each email before sending
✅ Document source of each email
✅ Note contact name and title
✅ Get explicit owner approval
✅ Check for bounces after sending
