# ❄️ CAMPAIGN: OPERATION POLK COOLING (HVAC)

**Status:** DRAFTING
**Target:** HVAC & AC Repair Owners
**Region:** Polk County, FL (Lakeland, Davenport, Winter Haven)
**Ticket:** $497/mo (Missed Call Text Back + AI Booking)

---

## ✅ PHASE 1: PRE-FLIGHT CHECKLIST (THE "MUST HAVES")

Before a single email is sent, these assets **MUST** be live and verified.

### 1. The Landing Zone (Conversion Page)

* [ ] **URL:** `hvac.aiserviceco.com` (or similar subdomain).
* [ ] **Headline:** "Stop Losing AC Repair Jobs to Missed Calls."
* [ ] **VSL (Video Sales Letter):** A 60s Loom video showing the "Missed Call Text Back" in action *specifically* for an AC company.
* [ ] **The Offer:** 14-Day Free Trial (No Credit Card) OR $497/mo direct sign-up.
* [ ] **Call to Action:** Two Buttons.
  * Primary: "Start My Free Trial" (Goes to GHL Payment Form).
  * Secondary: "Get a Demo" (Goes to Calendly).

### 2. The Banking (Payment Infrastructure)

* [ ] **Stripe Product:** Created product "AI Receptionist - HVAC" ($497/mo).
* [ ] **GHL Order Form:** Embedded on the Landing Page.
* [ ] **Terms of Service:** Checkbox for "I agree to SMS charges" (Critical for FTSA Compliance).

### 3. The Automation (GHL Workflows)

* [ ] **Calendar:** "Discovery Call" calendar configured.
* [ ] **Phone Numbers:** A dedicated Twilio number with a local FL area code (e.g., 863) increases trust.
* [ ] **Unsubscribe Logic:** "STOP" keyword must immediately tag `DND` and remove from all workflows.

---

## ⚔️ PHASE 2: THE SPARTAN SEQUENCE (CADENCE)

**Trigger:** Contact Tagged `campaign-hvac-polk` inside GHL.

### Day 1: The "Predator" Hook (Email)

* **Subject:** *missed calls at [Company Name]*
* **Body:** "hey [Name], fast question. i just called [Company Name] and it went to voicemail. i tested 5 other HVAC guys in lakeland and 3 of them texted me back instantly with a booking link. you're losing jobs to them right now. i recorded a 30s video showing how to fix this. want the link?"
* **Goal:** Reply "Yes".

### Day 1 (2 Hours Later): The "Nudge" (SMS)

* **Body:** "hey [Name], sent you an email about those missed calls. let me know if you want that video. - [My Name]"

### Day 2: The "Value" (Email)

* **Subject:** *video for [Company Name]*
* **Body:** "hey [Name], didn't hear back, but figured this was too important. here is that video showing how the 'Missed Call Text Back' system captures the lead before they call the next guy on google. [LINK TO LANDING PAGE]. takes 5 mins to setup."
* **Goal:** Click Link.

### Day 5: The "Soft Nudge" (SMS)

* *Strict FTSA Compliance: Only send if they replied/opted-in previously OR if using "Legitimate Interest" (risky). Better to stick to Email until they engage.*
* **Alternative Email:** "did you see the video? thoughts?"

### Day 7: The "Breakup" (Email)

* **Subject:** *crossing you off?*
* **Body:** "hey [Name], assuming you're set on appointments or just busy fixing ACs. i'm going to archive this thread so i don't bug you. if you ever want to stop leaking leads, the link is here: [LINK]. best of luck."

### Day 14: The "Zombie" Revival (Email)

* **Subject:** *one last idea*
* **Body:** "hey, saw a competitor in davenport just installed this. they recovered $4k in jobs last week just from missed calls. thought you should know."

### Monthly: The "Market Update" (Newsletter)

* **Content:** "HVAC Marketing Trends in Florida". Value-first, low pitch.
* **Footer:** "Unsubscribe" link clearly visible.

---

## 🛠️ PHASE 3: TECHNICAL IMPLEMENTATION

### 1. Configure the AI Architect

I need to update `workflow_architect.py` to generate this *exact* JSON structure so you can import it into GHL.

### 2. Run the Scout

We need to gather the first batch of 50 Leads.

* **Action:** Run `run_target.py` on a list of Google Maps results.

**Approvals Needed:**

1. Does the **Day 1 Hook** sound like you?
2. Do you have the **Landing Page** URL ready?
