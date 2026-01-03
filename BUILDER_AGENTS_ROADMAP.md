# PROJECT: THE CONSTRUCTOR (BUILDER AGENTS)

## 1. THE VISION

Automated "Digital Real Estate" construction. Instead of manually dragging elements in GHL, we deploy agents to build the infrastructure.

## 2. THE AGENTS

### 🏗️ AGENT 1: FUNNEL FORGE (The Designer)

- **Role**: Creative Director & Engineer.
- **Input**: "Build a Dentist Lander in Miami."
- **Process**:
  1. **Gemini**: Writes Headline, Subheadline, Benefits, and Call to Action.
  2. **Gemini**: Generates specific HTML/Tailwind instructions.
  3. **Execution**:
      - *Option A (API)*: Creates a new Funnel Step > Injects code into "Custom HTML" element.
      - *Option B (Browser)*: Logs in regarding `ghl_browser.ts` > Selects a template > Updates text dynamically.
- **Output**: A live URL ready for traffic.

### 🔌 AGENT 2: WIRING TECH (The Engineer)

- **Role**: Backend Configuration.
- **Capabilities**:
  - **Trigger Links**: Auto-generates "Click to Call" or "Click to Book" tracking links.
  - **Forms**: Creates "Qualified Lead" forms (Name, Email, Phone, "Are you ready?").
  - **Workflows**: Builds the "Nurture Sequence" automations (SMS 1 -> Wait -> SMS 2).
- **Tech**: 100% GHL API v2.

## 3. IMPLEMENTATION PLAN

### PHASE 1: The Blueprint (Next Session)

- Create `modules/constructor/funnel_forge.py`.
- Define the `generate_funnel_copy(niche)` function using Gemini.

### PHASE 2: The Hookup

- Create `modules/constructor/wiring.py`.
- Define `create_trigger_link(url, name)` via API.

## 4. IMMEDIATE NEXT STEP

We need to verify if your GHL API Token (`pit-8c6...`) has `Funnels.ReadWrite` and `Workflows.ReadWrite` scopes.
