---
description: Query the AI board for strategic decisions and analysis
---

# Board Protocol Workflow

// turbo-all

## Purpose

Query Claude, Grok, Gemini, and ChatGPT simultaneously for strategic decisions, capability assessments, or problem analysis.

> [!CAUTION]
> **When Dan invokes /board_protocol, the agent MUST:**
>
> 1. QUERY THE BOARD FIRST before taking any action
> 2. WAIT for board responses
> 3. SYNTHESIZE recommendations
> 4. PRESENT to Dan for approval BEFORE implementing anything
>
> **DO NOT act unilaterally. Investigation = Board investigates, not agent.**

## Complete Steps (MANDATORY)

### Step 1: Update the Prompt

Edit `scripts/board_call_raw.py` and update the `PROMPT` variable with the question or investigation topic.

### Step 2: Run the Board Query

```bash
cd c:\Users\nearm\.gemini\antigravity\scratch\empire-unified
python scripts/board_call_raw.py
```

### Step 3: Review All Responses

Open `board_call_raw.json` and check:

- [ ] Claude responded (if not, check ANTHROPIC_API_KEY credit balance)
- [ ] Grok responded (if not, check GROK_API_KEY)
- [ ] Gemini responded (if not, check GEMINI_API_KEY)
- [ ] ChatGPT responded (if not, check OPENAI_API_KEY)

**CRITICAL:** If any board member is missing, INFORM DAN immediately.

### Step 4: Synthesize Board Recommendations

Create a summary table:

| AI | Key Recommendation | Confidence |
|----|-------------------|------------|
| Claude | [summary] | [high/med/low] |
| Grok | [summary] | [high/med/low] |
| Gemini | [summary] | [high/med/low] |
| ChatGPT | [summary] | [high/med/low] |

### Step 5: Present to Dan for Approval

Use `notify_user` to present:

1. The synthesized recommendations
2. Areas of consensus
3. Areas of disagreement
4. Agent's recommendation
5. **Ask for approval before taking action**

### Step 6: Execute ONLY After Approval

Only proceed with implementation after Dan approves the recommended approach.

## Example Prompts

- "Should we build X feature? What are the tradeoffs?"
- "We're experiencing Y problem. What's the root cause?"
- "How would we implement Z? What's the best approach?"
- "Is this strategic direction correct or should we pivot?"
- "INVESTIGATION: [describe incident] - what went wrong and how to fix?"

## API Keys (Backup Reference)

Located in `knowledge_base/operational_memory.md` Section 13:

- ANTHROPIC_API_KEY (Claude)
- GROK_API_KEY (Grok/xAI)
- GEMINI_API_KEY (Google Gemini)
- OPENAI_API_KEY (ChatGPT)

## Notes

- All 4 AIs respond simultaneously
- Responses are saved to board_call_raw.json
- Takes ~30-60 seconds to complete all queries
- **Agent must NOT act without board consultation when this protocol is invoked**
