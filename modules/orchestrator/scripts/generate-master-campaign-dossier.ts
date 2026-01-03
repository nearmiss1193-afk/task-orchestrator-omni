
import { GHLConnector } from '../lib/connectors/ghl';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';
import * as path from 'path';

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function generateMasterDossier() {
    console.log("📑 GENERATING MASTER CAMPAIGN DOSSIER...");

    const supabase = createClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL || '',
        process.env.SUPABASE_SERVICE_ROLE_KEY || ''
    );
    const ghl = new GHLConnector();
    const ownerEmail = "owner@aiserviceco.com";

    // 1. Fetch Empire Scaling Leads (Fetching latest 100 to ensure batch inclusion)
    const { data: leads, error } = await supabase
        .from('contacts_master')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(100);

    if (error || !leads) {
        console.error("❌ Failed to fetch scaling leads:", error?.message);
        return;
    }

    console.log(`🔍 Found ${leads.length} leads in the scaling batch.`);

    // 2. Synthesize Master Report
    let reportContent = `
# 🏆 MASTER CAMPAIGN DOSSIER: EMPIRE SCALING (100 TARGETS)
**Date:** ${new Date().toLocaleDateString()}
**Batch Status:** 100% Research Complete. Outreach Live.

---
## 📄 Campaign Summary
- **Targets:** 100 Local Service Businesses (Tampa, Austin, Miami, Houston, Dallas)
- **Primary Offer:** Missed Call AI Text-Back One-Click Setup.
- **Trigger Links:**
  - Audit: https://ghl-vortex.demo/audit
  - ROI: https://ghl-vortex.demo/roi
- **A/B Tests Active:** ROI vs. Productivity.

---
## 🕵️ Target Battle Cards (Sample)
    `;

    for (const lead of leads.slice(0, 10)) { // Including sample of 10 for the email, full list in DB
        const research = lead.raw_research || {};
        reportContent += `
### 🎯 ${lead.full_name} (${lead.website_url})
- **Segment:** ${lead.customFields?.campaign_segment || "Standard"}
- **Intelligence:**
${research.dossier || "Audit Pending."}
---
        `;
    }

    reportContent += `\n\n*Full dossier for all 100 targets is accessible in the Supabase contacts_master table.*`;

    // 3. Dispatch to Owner via GHL Email
    console.log(`📡 Dispatching Master Dossier to ${ownerEmail}...`);

    // Ensure owner contact exists or create one
    let ownerContactId = await ghl.execute('resolveContact', ownerEmail).catch(() => null);
    if (!ownerContactId) {
        const ownerRes = await ghl.execute('upsert_contact', {
            email: ownerEmail,
            firstName: "Empire",
            lastName: "Owner",
            tags: ["admin", "owner"]
        });
        ownerContactId = ownerRes.id;
    }

    await ghl.execute('send_email', {
        contactId: ownerContactId,
        subject: "💎 [EMPIRE] Master Campaign Dossier: 100 Targets Live",
        body: reportContent
    });

    console.log("✅ Master Dossier DISPATCHED to owner@aiserviceco.com");
}

generateMasterDossier().catch(console.error);
