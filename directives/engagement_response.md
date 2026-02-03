# Directive: Engagement Response Protocol

## Goal

Monitor, classify, and respond to social media engagement (comments, DMs) to build brand awareness and drive conversions.

## Execution Scripts

- [engagement_monitor.py](file:///c:/Users/nearm/.gemini/antigravity/playground/empire-unified/execution/engagement_monitor.py) - 24/7 monitoring

## Polling Schedule

- **Comments**: Every 5 minutes via Ayrshare
- **DMs**: Every 5 minutes via GHL Conversations

## Intent Classification

| Intent | Priority | Auto-Response? |
|--------|----------|----------------|
| Booking | High | Yes - provide link |
| Pricing | High | Yes - share pricing |
| Question | Normal | Yes - answer if possible |
| Interest | Normal | Yes - provide CTA |
| Praise | Low | Yes - thank them |
| Complaint | Urgent | NO - escalate to human |
| Support | High | NO - escalate to human |
| Spam | Ignore | No response |

## Response Guidelines

1. **Keep it brief** - Under 280 characters when possible
2. **Be conversational** - Avoid corporate-speak
3. **Include CTA** - Always guide to next step
4. **Escalate negative** - Never auto-respond to complaints

## Escalation Triggers

- Sentiment: Negative
- Keywords: "refund", "lawsuit", "scam", "report"
- Intent: Complaint or Support
- Multiple messages from same user

## Self-Annealing Log

| Date | Error | Fix Applied | Outcome |
|------|-------|-------------|---------|
| (auto-populated) | - | - | - |
