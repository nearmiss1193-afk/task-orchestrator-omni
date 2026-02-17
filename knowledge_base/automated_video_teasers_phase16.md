# Learning: Automated Headless Teasers (Phase 16) — Feb 16, 2026

## What Happened

We implemented automated mobile-view website teasers to drive pattern interrupts in outreach. This required transitioning from static audits to dynamic video content.

## Technical Implementation

- **Stack**: Playwright (Async Python) + ffmpeg + Modal.
- **Watermark**: CSS injection for "SECURITY AUDIT" pattern interrupt.
- **Storage**: Direct upload to Supabase Storage (bypassing Ayrshare limits).

## Challenges & Solutions

### 1. Modal Image Dependencies

- **Problem**: Playwright video recording requires `ffmpeg`, which is not in the base slim images.
- **Result**: `capture_mobile_teaser` returned `None` silently because the video file was never created.
- **Fix**: Added `apt-get update && apt-get install -y ffmpeg` to the Modal `.run_commands()`.

### 2. Timeouts & Politeness

- **Problem**: page.goto() + 10s recording + upload exceeded standard 60s worker timeouts.
- **Fix**: Increased `research_strike_worker` timeout to 300s.

### 3. Missing Imports

- **Problem**: `NameError: os` and `NameError: time` in worker scripts due to fragmented imports.
- **Fix**: Standardized global imports at the top of `deploy_unified.py` and `audit_generator.py`.

## Actions Taken

- Unified `deploy.py` and `deploy_v2.py` logic into `deploy_unified.py`.
- Integrated `teaser_worker.py` into the enrichment cycle.
- Successfully verified with a 440KB mobile scroll of `aiserviceco.com`.

## Future Prevention

- **Rule**: Always include `ffmpeg` when using Playwright `record_video_dir`.
- **Rule**: Standardize `import time, os` in all Modal-entrypoint-adjacent modules to avoid serialisation "phantom" NameErrors.
