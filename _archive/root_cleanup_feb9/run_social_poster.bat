@echo off
REM Social Media Auto-Poster - Runs every 6 hours via Windows Task Scheduler
REM Created: 2026-01-11

cd /d C:\Users\nearm\.gemini\antigravity\scratch\empire-unified
python -m modal run modal_social.py >> social_post_log.txt 2>&1
echo [%date% %time%] Social post executed >> social_post_log.txt
