
require('dotenv').config({ path: '.env.local' });
import { createClient } from '@supabase/supabase-js';
import { MarketingAgent } from '../lib/marketing-agent';

const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

async function testMasterEnrichment() {
    console.log("🧪 Starting Contacts Master End-to-End Verification...");

    const dummyContact = {
        email: 'ceo@antigravity-demo.com',
        full_name: 'Antigravity CEO',
        website_url: 'https://example.com',
        ghl_contact_id: 'master_' + Date.now(),
        status: 'new'
    };

    console.log(`[Test] Step 1: Creating master contact...`);
    const { data: contactData, error: insertError } = await supabase
        .from('contacts_master')
        .insert(dummyContact)
        .select()
        .single();

    if (insertError) throw insertError;
    const contactId = contactData.id;

    console.log(`[Test] Step 2: Running MarketingAgent for contact ${contactId}...`);
    const agent = new MarketingAgent();
    await (agent as any).enrichContact(contactData);

    console.log(`[Test] Step 3: Verifying master table updates...`);
    const { data: finalRecord, error: fetchError } = await supabase
        .from('contacts_master')
        .select('*')
        .eq('id', contactId)
        .single();

    if (fetchError) throw fetchError;

    console.log("\n--- MASTER TEST RESULTS ---");
    console.log("Status:", finalRecord.status);
    console.log("Lead Score:", finalRecord.lead_score);
    console.log("Research Data:", JSON.stringify(finalRecord.raw_research, null, 2).slice(0, 500) + "...");
    console.log("AI Strategy:\n", finalRecord.ai_strategy);
    console.log("--------------------\n");

    if (finalRecord.status === 'nurturing' && finalRecord.ai_strategy) {
        console.log("✅ SUCCESS: Master pipeline worked!");
    } else {
        console.log("❌ FAILURE: Master pipeline failed verification.");
    }

    await supabase.from('contacts_master').delete().eq('id', contactId);
    process.exit(0);
}

testMasterEnrichment().catch(err => {
    console.error("❌ Test failed:", err);
    process.exit(1);
});
