# Omni-Automation Agent Dossier

This document outlines the specialized AI agents operating within the Omni-Automation system, including mission-critical prompts and architectural patterns.

---

## 1. Acquisition Agents ("The Predators")

These agents handle the heavy lifting of finding leads and initiating outreach.

### THE "PREDATOR" AGENT (Scraping & Multi-Channel Outreach)

Handles finding leads across SMS, Email, and Social DMs.

- **Mission Prompt**:
  > "MISSION: Find 50 HVAC companies in Florida and start the outreach loop.
  > Use the browser to search Google Maps/Yelp for 'HVAC Florida'. Scrape Company Name, Website, and Phone Number. Save leads to Supabase `contacts_master`.
  > Multi-Channel Loop: Step A: Send a personalized Email via the GHL API. Step B: Wait 24 hours; if no reply, send a follow-up SMS. Step C: Find their Facebook page and send a DM using the GHL Social API.
  > Self-Anneal: If a phone number is a landline (fails SMS), tag it as 'Voice-Only' and notify me."

### THE GOOGLE MAPS SCAPER

End-to-end GMaps lead generation pipeline.

- **Mission Prompt**:
  > "MISSION: Build me an end-to-end Google Maps lead generation pipeline.
  > Scrape businesses from Google Maps using Apify. Enrich each with deep contact extraction from their websites using Claude 3.5 Haiku. Save to a Google Sheet with 36 columns of structured data including owner info and team contacts. Implement MD5 deduplication."

### INSTANTLY CAMPAIGN WRITER

Automates cold email campaign creation in Instantly.ai.

- **Mission Prompt**:
  > "MISSION: Create 3 cold email campaigns in Instantly based on client offers. Generate 3 steps per campaign. Step 1 must have 2 A/B variants. All bodies must be HTML formatted. Use America/Chicago timezone for scheduling."

---

## 2. Fulfillment Agents ("The Ghosts")

These agents ensure delivery, response, and client satisfaction.

### THE "GHOST" AGENT (Response Handler)

Lives inside GHL Conversations via API to ensure no lead is ignored.

- **Mission Prompt**:
  > "MISSION: Monitor GHL Conversations 24/7. Poll the GHL API every 5 minutes for new messages. Use research data from Supabase to draft context-aware responses. If they ask for a meeting, book it on my GHL Calendar. If they say 'Stop', tag as 'Unsubscribed'."

### CREATIVE DIRECTOR ROLE

Converts raw data into short-form video and social posts.

- **Tools**: Browser Actuation for RunwayML/Pika (Video), ElevenLabs (Voice), and GHL Social Planner.
- **Mission Prompt**:
  > "MISSION: Create a 30-second promo video for a new lead. Scrape the lead's website for hero images/colors. Use RunwayML for 'Pan and Zoom' effects. Use ElevenLabs for voiceover. Combine via ffmpeg and upload to GHL Social Planner."

### SNAP DEPLOYER

Onboards new clients in 60 seconds.

- **Mission Prompt**:
  > "MISSION: Build the Snap Deployer. Create sub-account in GHL, load 'Master Agency Snapshot', auto-fill custom values, purchase a local Twilio number, and output the login link."

### DESCRIPT VIDEO AGENT

Automates high-quality video production.

- **Mission Prompt**:
  > "MISSION: Activate Descript Video Agent. Ingest script from Content Predator, use Overdub for voice cloning, insert stock b-roll, render 1080p, and save URL to Supabase."

---

## 3. Specialist & Meta-Agents

The "glue" that scales a 7-figure agency.

### LAZARUS LOOP (Database Reactivation)

Wakes up dead lead lists with "Spartan" yes/no questions.

### 5-STAR DEFENSE (Reputation Manager)

Automates Google Reviews based on sentiment analysis of completed services.

### VOICE CONCIERGE

Integrates VAPI.ai for outbound AI calling when leads don't book immediately.

### SOCIAL SNIPER

Automates Instagram/LinkedIn DMs and comments via GHL.

### FUNNEL ARCHITECT

Auto-builds industry-specific landing pages in GHL via snapshots.

---

## 4. Meta-Layer Controls

- **QA Agent**: Removes "AI-isms" (e.g., "delve", "tapestry") from all outgoing copy.
- **Profit Maximizer**: Calculates ROI scores; alerts human if lead value >$1M.
- **Maintenance Agent**: Monitors webhooks/APIs; auto-heals if UI changes.
- **ROI Telemetry**: Generates weekly reports on hook performance and channel ROI.
