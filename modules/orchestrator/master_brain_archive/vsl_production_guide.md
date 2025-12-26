# Spartan VSL: Production Guide

Turn your VSL Blueprint into a high-conversion MP4 video using AI generation tools.

## 1. The Production Stack

Recommended tools for the final render:

- **Visuals**: [Runway Gen-2](https://runwayml.com/) or [Luma Dream Machine](https://lumalabs.ai/dream-machine)
- **Voiceover**: [ElevenLabs](https://elevenlabs.io/) (Use "Marcus" or "Sorento" for a gritty Spartan tone)
- **Assembly**: [CapCut](https://www.capcut.com/) or [Canva Video](https://www.canva.com/video-editor/)

## 2. Step-by-Step Instructions

### Step A: Generate the Voiceover

1. Copy the script from the [VSL Plan](file:///C:/Users/nearm/.gemini/antigravity/brain/d91de16e-14b7-4513-a02b-aee6e62b91d0/implementation_plan_vsl.md).
2. Paste into **ElevenLabs**.
3. Settings: Stability 40%, Clarity 75%, Style Exaggeration 20%.
4. Download the `.mp3`.

### Step B: Animate the Storyboard

1. Upload the frames from your [Walkthrough](file:///C:/Users/nearm/.gemini/antigravity/brain/d91de16e-14b7-4513-a02b-aee6e62b91d0/walkthrough.md) to **Runway Gen-2** (using Image-to-Video).
2. Use these motion prompts:
   - **Frame 1 (The Leak)**: "Slow cinematic zoom into the cracks, glowing liquid cash flowing with high fluid dynamics."
   - **Frame 2 (The Engine)**: "Camera pan across the 3D circuit board, blue data pulses zipping through glass pipes."
   - **Frame 3 (The Scale)**: "Cinematic flyover across a digital map of Florida, neon pulses expanding across the coast."

### Step C: Final Assembly

1. Drop the VO and the generated video clips into **CapCut**.
2. Add kinetic typography (Bold, White, All-caps) sync'd to the voiceover.
3. **Background Music**: Dark, industrial, fast-paced cinematic drum track.

## 3. Deployment

Once the MP4 is ready, upload it to YouTube (Unlisted) or Vimeo and paste the link in your [GHL Nurture Template](file:///C:/Users/nearm/.gemini/antigravity/scratch/task-orchestrator/deploy.py) (`vsl-explainer` endpoint).
