
# 🎬 VEO 3 EXPERT AGENT: SOP

**Objective:** Automate the creation of commercial video assets using Google Veo (via VideoFX).

## 1. The Agent (`veo_pilot.py`)

This script uses **Playwright** to drive the browser. It is designed to:

1. Launch a persistent browser session (saving your login).
2. Navigate to Google VideoFX.
3. Type your prompts for Scene 1 and Scene 3.
4. Allow you to manually download the results.

## 2. Setup

Before running, ensure dependencies are installed:

```bash
pip install playwright
playwright install
```

## 3. Execution

Run the agent from your terminal:

```bash
python modules/media/veo_pilot.py
```

## 4. Operational Flow

1. **Login Gate:** The browser will open. If you are not logged in, log in to Google.
2. **Confirmation:** Press `ENTER` in the terminal once you see the "Create" interface.
3. **Typer:** The agent will type the prompt for **Scene 1** ("Sweaty Contractor").
4. **Generate:** Checks for the generate button. If it fails, click "Generate" yourself.
5. **Wait:** It waits 30 seconds for video generation.
6. **Next:** Press `ENTER` to move to Scene 3 ("Happy Contractor").

## 5. The Prompts (Hardcoded)

* **Scene 1:** "Cinematic, photorealistic handheld video of a sweaty HVAC contractor..."
* **Scene 2:** (Skipped - Use `dashboard_recovery.png`)
* **Scene 3:** "A confident, happy HVAC technician in a clean uniform..."

## 6. Output

Download your videos manually from the VideoFX interface. Drag them into your editor (Descript, Veo, etc.).
