---
description: Query the AI board for strategic decisions and analysis
---

# Board Protocol Workflow

// turbo-all

## Purpose

Query Claude, Grok, Gemini, and ChatGPT simultaneously for strategic decisions, capability assessments, or problem analysis.

## Steps

1. Navigate to empire-unified directory

```bash
cd c:\Users\nearm\.gemini\antigravity\scratch\empire-unified
```

1. Update the PROMPT in board_call_raw.py with your question

```bash
# Edit scripts/board_call_raw.py - change the PROMPT variable
```

1. Run the board query

```bash
python scripts/board_call_raw.py
```

1. Review responses in JSON file

```bash
# Open board_call_raw.json to see all responses
```

1. Synthesize board responses and take action

## Example Prompts

- "Should we build X feature? What are the tradeoffs?"
- "We're experiencing Y problem. What's the root cause?"
- "How would we implement Z? What's the best approach?"
- "Is this strategic direction correct or should we pivot?"

## Notes

- All 4 AIs respond simultaneously
- Responses are saved to board_call_raw.json
- Takes ~30-60 seconds to complete all queries
