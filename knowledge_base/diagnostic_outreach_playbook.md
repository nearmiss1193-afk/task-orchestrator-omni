# Personalized Diagnostic Report Outreach - HVAC B2B Best Practices

> [!IMPORTANT]
> This playbook is optimized for **HVAC/Home Services B2B outbound** using personalized diagnostic reports.

## Subject Lines (Email) - High Performers

| Type | Template | Example |
|------|----------|---------|
| **Direct + Personal** | `{{FirstName}}, your HVAC efficiency report is ready` | `Mike, your HVAC efficiency report is ready` |
| **Problem + Solution** | `Quick fix for {{CompanyName}}'s reviews` | `Quick fix for CoolAir Co's reviews` |
| **Competitive** | `{{CompanyName}} vs Industry: Key findings` | `CoolAir Co vs Industry: Key findings` |
| **Curiosity** | `Noticed something about your HVAC site…` | Same |
| **Value Hook** | `3 quick wins for {{CompanyName}} (free report)` | `3 quick wins for CoolAir Co (free report)` |

---

## SMS Openers - Proven Converters

### Pattern: Name + Company + Value Hook + Link

```
Hi {{Name}}, found 3 ways {{CompanyName}} can get more HVAC leads. Free report: [link]
```

```
Hi {{Name}}, saw an issue in {{CompanyName}}'s HVAC marketing – quick report: [link]
```

```
Hi {{Name}}, I analyzed your HVAC website (found 5 quick fixes). Mind if I send over the report?
```

### Key Rules

- **Always use prospect name + company**
- **Lead with value teaser** (not "we are XYZ company")
- **Keep under 160 chars** for SMS
- **Include link or offer to send**

---

## Email Body Copy - Optimal Structure

### Length: 3-5 sentences max

### FORBIDDEN

- Long intros ("Hope this finds you well...")
- Company background paragraphs
- Multiple CTAs
- Jargon

### REQUIRED Structure

1. **Line 1:** Personal greeting + what you found
2. **Line 2:** Specific pain point tied to business impact
3. **Line 3:** The deliverable (report) + CTA

### Example

> Hi Sarah – I ran a quick HVAC marketing report for CoolAir Co. It looks like your Google ranking is missing some easy wins (you're not ranking for several local keywords, which could mean lost customers). I put the findings and 3 fixes in a custom report for you.
>
> ➜ [View Your Report]

---

## CTA Best Practices

| ✅ DO | ❌ DON'T |
|-------|----------|
| `View My HVAC Report` | `Click Here` |
| `See Your Improvement Plan` | `Submit` |
| `Get the Free Report` | `Download` |

- **Single CTA per message**
- **Personalize:** "Your" / "My" makes it feel tailored
- **Position immediately after value preview**
- **Optional urgency:** "Report available through Friday"

---

## Report Preview Techniques

### Visual: Embed thumbnail/chart in email

- Score gauge (67/100)
- Bar chart: "Your Response Time vs Industry"
- Screenshot with markup

### Text Snippet: Key finding bullets

```
📊 Snapshot from your report:
• Your average job response time: 2.4 hours (industry avg: 1 hour) – costing ~15% of leads
• Google reviews: 3.8★ (HVAC norm: 4.5★) – quick fix: automated review requests
```

---

## Multi-Touch Follow-Up Sequence

| Touch | Timing | Channel | Message Theme |
|-------|--------|---------|--------------|
| 1 | Day 0 | Email | Report offer + preview |
| 2 | Day 2 | SMS | "Did you see the report I sent?" |
| 3 | Day 4 | Email | New insight + reminder |
| 4 | Day 7 | Email | "Worth a quick chat?" |

### Follow-up Template
>
> Hi John, just circling back – we saved that custom HVAC report for you. It highlights some quick wins (like boosting your Yelp rating). Let me know if you're interested – happy to resend the link or chat through any questions.

---

## Proven Case Study Results

| Metric | Result |
|--------|--------|
| Free audit emails (150) | 22 replies (14.7%), 5 calls, 2 clients |
| Scaled outreach (177K) | 200 replies, 50 leads, 3 deals week 1 |

> "Most people try to sell immediately in cold email. We lead with value first. That's the difference between spam and pipeline."

---

## High-Conversion HVAC SMS Variants (Jan 18 Launch)

### Variant 1: `hvac_sms_diagnostic_v1`

```
Hi {{name}}, noticed {{company}} might be losing calls to slow follow-up. We built a free report with 3 fixes. Want me to send it? -Sarah
```

### Variant 2: `hvac_sms_review_v1`

```
Hi {{name}}, your HVAC reviews are at 3.8★ (industry avg 4.5). Quick report shows how to fix that – interested? {{booking_link}}
```

### Variant 3: `hvac_sms_competitor_v1`

```
Hi {{name}}, ran a quick analysis of {{company}} vs your top competitor. Found 2 easy wins. Free report: {{booking_link}} -Sarah
```

### Variant 4: `hvac_sms_response_v1`

```
Hi {{name}}, businesses responding within 5 min convert 5x more. How fast is {{company}}? Free audit report here: {{booking_link}}
```

### Variant 5: `hvac_sms_curiosity_v1`

```
Hi {{name}} – noticed something interesting about {{company}}'s HVAC marketing. 2 min to share? -Sarah from AI Service Co
```

---

## High-Conversion HVAC Email Templates

### Template 1: `hvac_email_report_v1`

**Subject:** `{{firstName}}, your HVAC efficiency report is ready`

> Hi {{firstName}},
>
> I ran a quick marketing report for {{company}}. Found 3 things that might be costing you leads:
>
> 1. Response time is 2x industry average
> 2. Missing key local SEO terms
> 3. Review score below competitor average
>
> Full report + fixes: [View Your Report]
>
> Happy to walk through it if helpful.
> – Sarah

### Template 2: `hvac_email_competitive_v1`

**Subject:** `{{company}} vs. Industry: Key findings inside`

> Hi {{firstName}},
>
> I compared {{company}} to the top 5 HVAC companies in your area.
>
> You're winning on: service variety, website design.
> You're behind on: response time, Google reviews.
>
> [See the Full Comparison]
>
> Worth 5 min of your time if you're looking to grow.
> – Sarah

---

## Safety & Compliance

- **Always include opt-out** (STOP for SMS)
- **Verify consent** before SMS
- **No payment collection** via SMS/voice
- **Track all outreach** in `outreach_attribution`
