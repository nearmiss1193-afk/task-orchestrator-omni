# AEO Live Deployment Guide

This guide explains how to move the AI Visibility Audit (AEO) system from the `playground` to the `live` Modal-backed system.

## 1. Playground Sync

Ensure all local scripts are updated to include Similar Web / Manus AI data points.

- [x] `execution/enrich_leads.py` now includes `aeo_data` (traffic, revenue range).
- [x] `execution/aeo_auditor.py` is capable of consuming this data for report generation.

## 2. Live System Update

The `deploy.py` script has been updated with:

- `MISSION: AI VISIBILITY AUDIT (AEO) REPORT GENERATION`
- Enhanced `research_lead_logic` to identify the "AI Gap" using Gemini.

## 3. How to Deploy to Live

Run the deployment script from your terminal:

```powershell
python run_deploy.py
```

This will push the new AEO missions to Modal.

## 4. Triggering Audits in Live

To trigger an audit for a specific contact in GHL:

1. Tag a contact in GHL with `trigger-vortex`.
2. The `research_lead_logic` will automatically analyze the site for AEO gaps.
3. Use the `aeo_audit_report` remote function (via Modal Dashboard or Script) to generate the MD report for that contact.

## 5. Sales Workflow

- **Hook**: Use the updated Spartan Response hook: *"saw your competitor is getting all the chatgpt traffic for solar in hawaii. ran an audit for you."*
- **Audit**: Provide the generated AEO report as a high-value "Foot in the Door".
- **Fulfillment**: Follow the "3 Pillars" in `directives/aeo_audit_directive.md`.
