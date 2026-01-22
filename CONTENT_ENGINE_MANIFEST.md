# Content Engine & Social Command Center

## System Overview

Autonomous content creation, distribution, and engagement system for AI agency operations.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTENT ENGINE                                │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 1: CONTENT GENERATION                                     │
│  ├── veo_visionary.py      → AI video generation (Gemini/Veo)   │
│  ├── creatomate_studio.py  → Cloud video editing (REST API)     │
│  ├── inspix_creator.py     → Browser automation for Inspix.io   │
│  ├── blog_generator.py     → AI blog creation with SEO          │
│  └── newsletter_engine.py  → Email campaigns via GHL            │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: DISTRIBUTION                                           │
│  ├── social_distributor.py → Ayrshare (13 platforms) + GHL      │
│  └── Platforms: Facebook, Instagram, Twitter/X, LinkedIn,       │
│      YouTube, TikTok, Pinterest, Reddit, Telegram, Threads,     │
│      Google Business Profile, Snapchat, Bluesky                  │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: ENGAGEMENT                                             │
│  └── engagement_monitor.py → Comment/DM polling, sentiment      │
│      analysis, auto-response, escalation to humans              │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 4: ANALYTICS                                              │
│  └── Supabase tables: content_library, social_posts,            │
│      social_comments, social_dms, content_performance           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Execution Scripts

### 1. veo_visionary.py

**Purpose:** AI video generation using Google Veo via Gemini API

**Capabilities:**

- Text-to-video (8s clips, 720p-4K)
- Image-to-video with motion effects
- Budget control ($20 max per video)
- Auto-save to content library

**Key Functions:**

```python
generate_from_text(prompt, duration=8, resolution="1080p", aspect_ratio="16:9")
generate_from_image(image_path, prompt, motion_type="pan_zoom")
generate_ad_video(product_description, style="cinematic")
```

**Env Vars:** `GOOGLE_API_KEY`

---

### 2. creatomate_studio.py

**Purpose:** Cloud video editing via Creatomate REST API

**Capabilities:**

- Template-based rendering
- JSON-based video creation (no template needed)
- Auto-captions and text overlays
- Multi-platform export presets

**Key Functions:**

```python
render_from_template(template_id, modifications)
render_from_json(source, platform="youtube")
create_text_video(text, duration=5.0, platform="instagram_reels")
create_video_with_caption(video_url, caption_text)
render_for_all_platforms(template_id, modifications)
```

**Export Presets:**

| Platform | Resolution | Aspect |
|----------|------------|--------|
| youtube | 1920x1080 | 16:9 |
| instagram_feed | 1080x1080 | 1:1 |
| instagram_reels | 1080x1920 | 9:16 |
| tiktok | 1080x1920 | 9:16 |
| twitter | 1280x720 | 16:9 |

**Env Vars:** `CREATOMATE_API_KEY`

---

### 3. inspix_creator.py

**Purpose:** Browser automation for Inspix.io (no API available)

**Capabilities:**

- Queue generation requests
- Generate browser task instructions
- Track downloads in content library

**Key Functions:**

```python
generate_browser_instructions(prompt, output_type="video")
get_browser_task(prompt, output_type="video")
queue_generation(prompt, output_type="video", priority="normal")
```

**Note:** Requires browser subagent to execute tasks

---

### 4. social_distributor.py

**Purpose:** Multi-platform social media posting

**Capabilities:**

- Post to 13 platforms via Ayrshare
- Fallback to GHL Social Planner
- Platform-specific content optimization
- Scheduled posting and weekly automation
- Comment retrieval and reply

**Key Functions:**

```python
post(text, platforms, media_url=None, schedule_time=None, hashtags=None)
post_to_ayrshare(text, platforms, media_url=None)
post_to_ghl(text, platforms, media_url=None)
schedule_week(posts, start_date=None)
get_analytics(post_id)
get_comments(post_id)
reply_to_comment(post_id, comment_id, reply_text, platform)
```

**Platform Limits:**

| Platform | Text Limit | Notes |
|----------|-----------|-------|
| Twitter | 280 chars | Max 4 media |
| Instagram | 2200 chars | Max 30 hashtags |
| LinkedIn | 3000 chars | Max 9 media |
| TikTok | 2200 chars | Max 180s video |

**Env Vars:** `AYRSHARE_API_KEY`, `GHL_API_KEY`, `GHL_LOCATION_ID`

---

### 5. engagement_monitor.py

**Purpose:** 24/7 social listening and response

**Capabilities:**

- Poll comments every 5 minutes
- Poll GHL conversations for DMs
- Sentiment analysis (Gemini-powered)
- Intent classification
- Auto-response for safe categories
- Escalation for complaints/support

**Intent Categories:**

| Intent | Priority | Auto-Response? |
|--------|----------|----------------|
| booking | High | Yes |
| pricing | High | Yes |
| question | Normal | Yes |
| interest | Normal | Yes |
| praise | Low | Yes |
| complaint | Urgent | NO - human |
| support | High | NO - human |
| spam | Ignore | No |

**Key Functions:**

```python
analyze_message(text)  # Returns sentiment, intent, priority
process_new_engagement()  # Poll all sources
get_pending_responses(priority=None, limit=10)
generate_response(message, context=None)
respond_to_comment(post_id, comment_id, response_text, platform)
run_monitor_loop(duration_minutes=60)
```

**Env Vars:** `AYRSHARE_API_KEY`, `GHL_API_KEY`, `GOOGLE_API_KEY`

---

### 6. blog_generator.py

**Purpose:** AI-powered blog creation with SEO

**Capabilities:**

- 4 blog templates
- SEO meta generation (title, description, slug)
- Video embedding
- CTA insertion
- Blog series generation

**Templates:**

| Template | Tone | Words |
|----------|------|-------|
| ai_tips | Helpful, conversational | 800 |
| industry_update | Professional, informative | 1000 |
| case_study | Storytelling with data | 1200 |
| how_to | Clear, instructional | 900 |

**Key Functions:**

```python
generate_blog(topic, template="ai_tips", keywords=None, video_url=None)
generate_series(theme, num_posts=4, keywords=None)
deploy_to_ghl(blog_id, location_id=None)
list_blogs(status=None)
quick_blog(topic, video_url=None)
```

**Env Vars:** `GOOGLE_API_KEY`

---

### 7. newsletter_engine.py

**Purpose:** Email campaign automation via GHL

**Capabilities:**

- 4 newsletter types
- Video thumbnail embedding
- HTML email templates
- GHL email campaign integration
- Drip sequence creation

**Newsletter Types:**

| Type | Subject Prefix |
|------|---------------|
| weekly_tips | 🤖 AI Tip of the Week: |
| product_update | 🚀 What's New: |
| case_study | 📈 Success Story: |
| ai_news | 🔮 AI Insights: |

**Key Functions:**

```python
generate_newsletter(topic, newsletter_type="weekly_tips", video_url=None)
send_via_ghl(newsletter_id, contact_list=None, schedule_time=None)
create_drip_sequence(theme, num_emails=5, days_between=3)
list_newsletters(status=None)
quick_newsletter(topic, video_url=None)
```

**Env Vars:** `GHL_API_KEY`, `GHL_LOCATION_ID`, `GOOGLE_API_KEY`

---

## Directives (SOPs)

| Directive | Purpose |
|-----------|---------|
| content_creation.md | Content generation pipeline SOP |
| social_distribution.md | Multi-platform posting rules |
| engagement_response.md | Comment/DM response protocol |
| blog_newsletter.md | Blog & newsletter content guidelines |

---

## Database Schema (Supabase)

```sql
-- Content Library
content_library (id, type, source, file_url, duration_seconds, performance, created_at)

-- Social Posts
social_posts (id, content_id, platform, platform_post_id, scheduled_at, posted_at, engagement, status)

-- Comments
social_comments (id, post_id, platform, author, content, sentiment, intent, responded, response)

-- DMs
social_dms (id, platform, contact_id, direction, content, sentiment, requires_response)

-- Performance
content_performance (id, content_id, total_views, total_likes, engagement_rate)
```

---

## Environment Variables

```env
# Content Generation
GOOGLE_API_KEY=xxx        # Veo + Gemini analysis
CREATOMATE_API_KEY=xxx    # Cloud video editing

# Distribution
AYRSHARE_API_KEY=xxx      # 13-platform posting
GHL_API_KEY=xxx           # GHL integration
GHL_LOCATION_ID=xxx       # GHL location
```

---

## Quick Start Examples

```python
# Generate an ad video
from veo_visionary import generate_ad_video
result = generate_ad_video("HVAC emergency repair", style="cinematic")

# Post to all platforms
from social_distributor import quick_post
result = quick_post("Check out our new AI service!", 
                    platforms=["facebook", "instagram", "twitter"])

# Generate a blog with video
from blog_generator import quick_blog
result = quick_blog("5 Ways AI Saves HVAC Companies Money", 
                    video_url="https://...")

# Create a newsletter
from newsletter_engine import quick_newsletter
result = quick_newsletter("This Week's AI Tip", video_url="https://...")

# Monitor engagement
from engagement_monitor import check_engagement
summary = check_engagement()
```

---

## Self-Annealing Integration

All scripts integrate with `annealing_engine.py`:

- Error capture and classification
- Retry with exponential backoff
- Directive updates with learned fixes
- Persistent error memory

---

## File Locations

```
empire-unified/
├── execution/
│   ├── veo_visionary.py
│   ├── creatomate_studio.py
│   ├── inspix_creator.py
│   ├── social_distributor.py
│   ├── engagement_monitor.py
│   ├── blog_generator.py
│   ├── newsletter_engine.py
│   └── annealing_engine.py
├── directives/
│   ├── content_creation.md
│   ├── social_distribution.md
│   ├── engagement_response.md
│   └── blog_newsletter.md
├── content_library/
│   ├── blogs/
│   └── newsletters/
├── scripts/
│   └── content_library_schema.sql
└── orchestrator_logs/
    ├── error_memory.json
    └── annealing_events.json
```
