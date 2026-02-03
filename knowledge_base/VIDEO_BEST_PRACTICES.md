# Video Creation Best Practices - Creatomate & Social Media Ads

## Creatomate API Integration

### API Credentials

```
CREATOMATE_API_KEY: e7bba778e22f43e9b0dcf6136f402e1ada336056d6360daf5239905c79eaa8d3f1e99558ab03f985ff3d66de4a5dfd2c
Template ID (Quick Promo): df44e51c-d1b1-49c3-97ed-55dce79a72b7
API Endpoint: https://api.creatomate.com/v2/renders
```

### Best Practices

1. **Use Template-Based Generation** (Recommended)
   - Design reusable templates in Creatomate editor
   - Use API to dynamically insert text, video, images
   - Ensures brand consistency at scale

2. **Key API Parameters**
   - `template_id`: Reference to your video design
   - `modifications`: Dynamic elements (text, images, video clips)
   - Use webhooks for render completion (don't poll)

3. **Fast Rendering for Testing**
   - Creatomate offers quick preview rendering
   - Test iteration before final render

---

## Platform-Specific Video Specs

### Facebook Ads

| Spec | Value |
|------|-------|
| **Duration** | 15-30 seconds (15sec ideal for feed) |
| **Format** | MP4, MOV |
| **Resolution** | 1080 x 1080 (square) or 1080 x 1350 (4:5 vertical) |
| **Aspect Ratio** | 1:1 (square) or 4:5 (vertical for mobile) |
| **Max File Size** | 4 GB |

### Instagram (Reels & Feed)

| Spec | Value |
|------|-------|
| **Duration** | 15-30 seconds |
| **Format** | MP4 |
| **Resolution** | 1080 x 1920 (9:16 vertical for Reels) |
| **Aspect Ratio** | 9:16 (Reels), 1:1 (Feed) |

### LinkedIn Video Ads

| Spec | Value |
|------|-------|
| **Duration** | 15-30 seconds (sweet spot) |
| **Format** | MP4 only |
| **Resolution** | 1080p recommended |
| **Aspect Ratio** | 16:9, 1:1, or 9:16 |
| **Max File Size** | 500 MB |

### YouTube/Google Ads

| Spec | Value |
|------|-------|
| **Duration** | 6 sec (bumper), 15-20 sec (action), 60+ sec (awareness) |
| **Format** | MP4 |
| **Resolution** | 1920 x 1080 (16:9) or 1080 x 1920 (9:16 Shorts) |
| **Aspect Ratio** | 16:9 (standard), 9:16 (Shorts) |

### TikTok

| Spec | Value |
|------|-------|
| **Duration** | 9-15 seconds (best engagement) |
| **Format** | MP4 |
| **Resolution** | 1080 x 1920 |
| **Aspect Ratio** | 9:16 (full vertical) |

---

## Content Strategy for HVAC B2B

### Video Types That Work

1. **Problem/Solution** (15 sec)
   - "Missing calls after 5pm? Here's how we fix that..."

2. **Social Proof** (20 sec)
   - Customer testimonial or case study result

3. **Before/After** (15 sec)
   - "Before: 40% calls answered. After: 100%"

4. **How It Works** (30 sec)
   - Simple 3-step explainer

### Winning Elements

- ✅ Text overlays (most watch without sound)
- ✅ Captions/subtitles always
- ✅ Clear CTA in last 3 seconds
- ✅ Mobile-first framing (vertical preferred)
- ✅ Hook in first 2 seconds

### Ad Copy Formulas

1. **Pain → Agitate → Solve**
   - "Missing calls? Every unanswered call is $200+ lost..."

2. **Question Hook**
   - "Who answers your phone at 9pm when an AC dies?"

3. **Number Hook**
   - "37% of HVAC calls go to voicemail..."

---

## Recommended Creatomate Templates for HVAC

1. **Quick Promo** (df44e51c-d1b1-49c3-97ed-55dce79a72b7)
   - Text + video overlay
   - Good for testimonials

2. **Social Proof** template
   - Stats + results display

3. **Before/After** template
   - Split screen comparison

---

## Automation Flow

```
1. Generate content (Gemini AI) → prompt variations
2. Create video (Creatomate API) → render with template
3. Store in content_library → pending approval
4. Approve (manual/auto) → content_approvals
5. Schedule post (posting_rules check) → content_queue
6. Publish (social_distributor) → social_posts
7. Monitor (engagement_monitor) → social_comments
8. Learn (update variant success) → prompt_variants
```

---

## Budget Guidelines

- Creatomate: ~$0.03-0.05 per render
- Facebook Ads: $5-20/day test budget
- LinkedIn Ads: $10-50/day (higher CPC, better B2B)
- Google/YouTube: $10-30/day

Start with 3-5 video variants, A/B test, scale winners.
