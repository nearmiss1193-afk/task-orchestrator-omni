# Content Engine Migration Manifest

## Source Location

`C:\Users\nearm\.gemini\antigravity\playground\empire-unified\`

## File Mapping

### Execution Scripts (→ execution/)

| Sandbox Path | Target Path | Description |
|--------------|-------------|-------------|
| execution/veo_visionary.py | execution/veo_visionary.py | AI video generation via Gemini/Veo |
| execution/creatomate_studio.py | execution/creatomate_studio.py | Cloud video editing (REST API) |
| execution/inspix_creator.py | execution/inspix_creator.py | Browser automation for Inspix.io |
| execution/blog_generator.py | execution/blog_generator.py | AI blog creation with SEO |
| execution/newsletter_engine.py | execution/newsletter_engine.py | Email campaigns via GHL |
| execution/social_distributor.py | execution/social_distributor.py | 13-platform posting via Ayrshare |
| execution/engagement_monitor.py | execution/engagement_monitor.py | Comment/DM polling + auto-response |
| execution/annealing_engine.py | execution/annealing_engine.py | Self-healing error handler |
| execution/anneal_wrapper.py | execution/anneal_wrapper.py | Annealing helper wrapper |
| execution/enrich_leads.py | execution/enrich_leads.py | Lead enrichment from web |
| execution/ghl_sync.py | execution/ghl_sync.py | GHL contact sync |
| execution/health_check.py | execution/health_check.py | System health verification |
| execution/competitor_research.py | execution/competitor_research.py | Competitor intel |
| execution/ux_audit.py | execution/ux_audit.py | Website UX analysis |
| execution/demo_report.py | execution/demo_report.py | Demo report generation |

### Directives (→ directives/)

| Sandbox Path | Target Path | Description |
|--------------|-------------|-------------|
| directives/content_creation.md | directives/content_creation.md | Content generation pipeline SOP |
| directives/social_distribution.md | directives/social_distribution.md | Multi-platform posting rules |
| directives/engagement_response.md | directives/engagement_response.md | Comment/DM response protocol |
| directives/blog_newsletter.md | directives/blog_newsletter.md | Blog & newsletter guidelines |
| directives/enrich_lead.md | directives/enrich_lead.md | Lead enrichment SOP |
| directives/account_audit.md | directives/account_audit.md | Account audit SOP |
| directives/browser_email.md | directives/browser_email.md | Browser email SOP |
| directives/ghl_funnel_creation.md | directives/ghl_funnel_creation.md | GHL funnel creation SOP |
| directives/integrity_guardian.md | directives/integrity_guardian.md | Data integrity checks |
| directives/spartan_response.md | directives/spartan_response.md | Rapid response protocol |

### SQL (→ sql/)

| Sandbox Path | Target Path | Description |
|--------------|-------------|-------------|
| scripts/content_library_schema.sql | sql/content_library_schema.sql | Content library tables + RLS |

### Content Library (→ content_library/)

| Sandbox Path | Target Path | Description |
|--------------|-------------|-------------|
| content_library/blogs/ | content_library/blogs/ | Generated blog storage |
| content_library/newsletters/ | content_library/newsletters/ | Generated newsletter storage |

---

## Required Environment Variables

```env
# Content Generation
GOOGLE_API_KEY=xxx        # Veo + Gemini AI
CREATOMATE_API_KEY=xxx    # Cloud video editing

# Distribution
AYRSHARE_API_KEY=xxx      # 13-platform social posting
GHL_API_KEY=xxx           # GoHighLevel integration
GHL_LOCATION_ID=xxx       # GHL location ID

# Database (already configured)
SUPABASE_URL=xxx
SUPABASE_KEY=xxx
```

---

## Migration Commands (PowerShell)

```powershell
# Set paths
$SRC = "C:\Users\nearm\.gemini\antigravity\playground\empire-unified"
$DST = "C:\Users\nearm\.gemini\antigravity\scratch\empire-unified"

# Create target directories
New-Item -ItemType Directory -Force -Path "$DST\execution"
New-Item -ItemType Directory -Force -Path "$DST\directives"
New-Item -ItemType Directory -Force -Path "$DST\content_library\blogs"
New-Item -ItemType Directory -Force -Path "$DST\content_library\newsletters"

# Copy execution scripts
Copy-Item "$SRC\execution\veo_visionary.py" "$DST\execution\"
Copy-Item "$SRC\execution\creatomate_studio.py" "$DST\execution\"
Copy-Item "$SRC\execution\inspix_creator.py" "$DST\execution\"
Copy-Item "$SRC\execution\blog_generator.py" "$DST\execution\"
Copy-Item "$SRC\execution\newsletter_engine.py" "$DST\execution\"
Copy-Item "$SRC\execution\social_distributor.py" "$DST\execution\"
Copy-Item "$SRC\execution\engagement_monitor.py" "$DST\execution\"
Copy-Item "$SRC\execution\annealing_engine.py" "$DST\execution\"
Copy-Item "$SRC\execution\anneal_wrapper.py" "$DST\execution\"
Copy-Item "$SRC\execution\enrich_leads.py" "$DST\execution\"
Copy-Item "$SRC\execution\ghl_sync.py" "$DST\execution\"
Copy-Item "$SRC\execution\health_check.py" "$DST\execution\"
Copy-Item "$SRC\execution\competitor_research.py" "$DST\execution\"
Copy-Item "$SRC\execution\ux_audit.py" "$DST\execution\"
Copy-Item "$SRC\execution\demo_report.py" "$DST\execution\"

# Copy directives
Copy-Item "$SRC\directives\*.md" "$DST\directives\"

# Copy SQL schema
Copy-Item "$SRC\scripts\content_library_schema.sql" "$DST\sql\"

# Copy original manifest
Copy-Item "$SRC\CONTENT_ENGINE_MANIFEST.md" "$DST\"

Write-Host "✅ Content Engine exported to $DST"
```

---

## Post-Migration Checklist

- [ ] Run `sql/content_library_schema.sql` in Supabase SQL Editor
- [ ] Add Creatomate API key to Modal secrets (if using video)
- [ ] Add Ayrshare API key to Modal secrets (for social posting)
- [ ] Test: `python execution/social_distributor.py --test`
- [ ] Test: `python execution/blog_generator.py --test`

---

## Files NOT Migrated (Decide Later)

These scripts/ files exist but are not core content engine:

- ab_test_tracker.py, lead_scorer.py, pipeline_analytics.py (analytics)
- Various mission-*.py files (prospecting)
- Various test-*.py files (dev/test)
