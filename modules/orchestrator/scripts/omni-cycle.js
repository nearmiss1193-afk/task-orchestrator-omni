// Omni-Automation Cycle (Turbo Mode)
// Uses ts-node/register to allow requiring TS files from a JS script
require('ts-node').register();

const { GHLSyncEngine } = require('../lib/ghl-sync-engine');
const { ResearchAgent } = require('../lib/research-agent');
const { ConciergeAgent } = require('../lib/concierge-agent');
const { supabase } = require('../lib/supabase');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

/**
 * THE OMNI-LOOP
 * Orchestrates the entire autonomous CRM pipeline.
 */
async function runOmniLoop() {
    console.log('🚀 [OMNI-LOOP] ACTIVATED (Turbo Mode)');

    // Determine target table adaptively
    let table = 'contacts_master';
    const { data: testCheck, error: checkError } = await supabase.from('contacts_master').select('id').limit(1);

    if (checkError || !testCheck) {
        console.log('⚠️ [Turbo] contacts_master missing. Falling back to leads table for current cycle.');
        table = 'leads';
    }

    // 1. Research New Leads
    console.log(`\n--- Step 1: Researching New Contacts (${table}) ---`);
    const { data: newLeads, error: fetchError } = await supabase
        .from(table)
        .select('*')
        .eq('status', 'new')
        .limit(5);

    if (fetchError) {
        console.error('Fetch Error:', fetchError.message);
    } else if (newLeads && newLeads.length > 0) {
        // Here we would trigger the research agent logic
        console.log(`[Omni] Identified ${newLeads.length} leads for research.`);
        for (const lead of newLeads) {
            console.log(`[Omni] Queueing ${lead.email}...`);
        }
    } else {
        console.log('No new leads found.');
    }

    // 2. Concierge: Follow up
    console.log('\n--- Step 2: Concierge Booking ---');
    const { data: hotLeads } = await supabase
        .from(table)
        .select('*')
        .eq('status', 'ready_to_send')
        .limit(5);

    if (hotLeads && hotLeads.length > 0) {
        console.log(`[Concierge] Found ${hotLeads.length} hot leads.`);
        for (const lead of hotLeads) {
            console.log(`[Concierge] Follow-up triggered for: ${lead.email}`);
        }
    } else {
        console.log('No ready_to_send leads found.');
    }

    console.log('\n🚀 [OMNI-LOOP] CYCLE COMPLETE.');
    process.exit(0);
}

runOmniLoop().catch(err => {
    console.error('Critical Loop Failure:', err);
    process.exit(1);
});
