# THE GHL AGENT ARSENAL (MASTER BLUEPRINT)

## 🏗️ CLASS: CONSTRUCTORS (The Builders)

These agents build the infrastructure.

1. **The Architect** (`modules/architect/main.py`): Creates Sub-Accounts & Loads Snapshots.
2. **Funnel Forge** (`modules/constructor/funnel_forge.py`): Writes Copy & HTML for Landers.
3. **Wiring Tech** (`modules/constructor/wiring.py`): Configures Links, Forms, and Workflows.

## 🛡️ CLASS: GUARDIANS (The Defenders)

These agents protect and maintain the business.
4. **Review Reclaimer** (`modules/guardians/reviews.py`): Monitors Google/FB Reviews. Responds instantly to boost SEO.
5. **The Governor** (`modules/guardians/governor.py`): already active in `deploy.py`. Self-heals system loops.

## ⚔️ CLASS: HUNTERS (The Sales Force)

These agents generate revenue.
6. **Spartan Responder** (Active): Text-back AI.
7. **Social Siege** (Active): LinkedIn/FB Poster.
8. **The Nexus** (`modules/hunters/voice_nexus.py`): Vapi.ai Outbound dialer for unbooked leads.
9. **The Saw** (`modules/hunters/cold_email.py`): Cold Email Blaster (Resend/Instantly).

## 📝 DEPLOYMENT QUEUE

To "Build All", we execute them in this order:

1. Wiring Tech (Quickest Win)
2. Review Reclaimer (High Trust)
3. Funnel Forge (Complex)
4. The Nexus (Advanced)
