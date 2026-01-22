# Mission: AEO Lead Sourcing

Use this prompt with Gemini or a similar LLM to identify high-value prospects for AI Visibility Audits.

## Prompt

```markdown
MISSION: AEO INTEL PREDATOR
ROLE: Professional Lead Generation Specialist for AI-Driven Marketing.

TASK:
Identify 20 high-potential businesses in [TARGET_CITY] within [TARGET_NICHE] that are currently "AI Invisible."

CRITERIA:
1. REVENUE: Must be in the $1M - $10M range (Established, staffed, and enough revenue to care about market share).
2. VISIBILITY GAP: They must be listed on page 1 of Google Maps but NOT recommended by ChatGPT/Perplexity when asked "Who are the best [TARGET_NICHE] in [TARGET_CITY]?"
3. TRAFFIC PROFILE: Look for signs of "Branding-Only" traffic (Old websites, lack of SEO content, but strong physical presence or billboards).
4. COMPETITIVE THREAT: Identify 1 competitor who IS getting recommended by AI in their area.

OUTPUT FORMAT (JSON):
[
  {
    "company_name": "",
    "website_url": "",
    "niche": "",
    "est_revenue": "",
    "ai_invisibility_reason": "e.g., No semantic schema, outdated service pages, or competitor [COMPETITOR] has more citations.",
    "competitor_stealing_traffic": ""
  }
]
```

## How to use

1. Copy the prompt above.
2. Replace `[TARGET_CITY]` and `[TARGET_NICHE]` (e.g., "Austin" and "Solar Installation").
3. Feed it to your research agent or use it manually in ChatGPT/Gemini.
4. Export the JSON to `execution/leads_[CITY].json` to begin the automated audit process.
