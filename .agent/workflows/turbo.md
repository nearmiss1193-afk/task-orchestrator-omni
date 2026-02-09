---
description: Turbo mode - auto-run all safe commands without asking for approval
---

# Turbo Mode

When the user activates `/turbo`, all subsequent commands should be executed with maximum speed and minimal friction.

// turbo-all

## Rules

1. Set `SafeToAutoRun: true` on ALL `run_command` calls that are read-only or non-destructive
2. Batch operations together when possible
3. Skip confirmations — execute and report results
4. Only pause for genuinely destructive operations (deleting production data, force-pushing to main)
5. Deploy commands, git commits, file moves, and app stops are all safe to auto-run in turbo mode
