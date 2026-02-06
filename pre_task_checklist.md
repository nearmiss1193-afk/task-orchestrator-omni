# PRE-TASK CHECKLIST

# Updated: Feb 5, 2026

# Purpose: Verify requirements before starting major tasks

## BEFORE EMAIL SENDING

- [ ] Verify recipient email address is researched (not guessed)
- [ ] Confirm total count with user ("You need X emails, correct?")
- [ ] Check working_commands.log for confirmed sending method
- [ ] Use Resend via reliable_email.py (NOT GHL - delivery issues)
- [ ] Draft content approved by owner

## BEFORE BOARD REVIEW

- [ ] Prompt updated in scripts/board_call_raw.py
- [ ] Include specific questions for board
- [ ] Run: python scripts/board_call_raw.py
- [ ] Check all 4 AI responses (Gemini may rate limit)

## BEFORE GIT OPERATIONS

- [ ] Run commands separately (no && in PowerShell)
- [ ] git add -A
- [ ] git commit -m "message"
- [ ] git push origin main --force

## BEFORE VERCEL DEPLOY

- [ ] cd public first
- [ ] vercel --prod --yes
- [ ] Verify <https://www.aiserviceco.com> after deploy

## BEFORE NOTIFY_USER

- [ ] Include dashboard link
- [ ] Include recovery commands
- [ ] Include what was done
- [ ] Include next steps

## TASK CONFIRMATION TEMPLATE

Before starting any multi-step task, say:
"Before I proceed, let me confirm:

- Task: [what you're doing]
- Count: [X items]
- Method: [how you'll do it]
- Correct?"

Wait for user confirmation before executing.

## QUICK REFERENCE

| Task | Command |
|------|---------|
| Send email | python send_approval_now.py |
| Board review | python scripts/board_call_raw.py |
| Git push | git add -A; git commit -m "msg"; git push origin main |
| Deploy | cd public; vercel --prod --yes |
| Session summary | python send_session_summary.py |
