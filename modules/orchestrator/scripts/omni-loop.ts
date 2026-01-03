import { GHLSyncEngine } from '../lib/ghl-sync-engine';
import { ResearchAgent } from '../lib/research-agent';
import { ConciergeAgent } from '../lib/concierge-agent';
import { supabase } from '../lib/supabase';
import * as dotenv from 'dotenv';
import * as path from 'path';

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
        const researcher = new ResearchAgent();
        for (const lead of newLeads) {
            console.log(`[Omni] Processing Lead: ${lead.email}`);
            // In Turbo mode, we assume the researcher handleResearch exists or we trigger research-loop logic
            // For now, logged for verification
        }
    } else {
        console.log('No new leads to research.');
    }

    // 2. Concierge: Follow up on Positive Sentiment
    console.log('\n--- Step 2: Concierge Booking ---');
    // Note: We use sentiment if available, else score
    const { data: hotLeads } = await supabase
        .from(table)
        .select('*')
        .or('sentiment.eq.positive,lead_score.gte.80')
        .eq('status', 'ready_to_send')
        .limit(5);

    if (hotLeads && hotLeads.length > 0) {
        const concierge = new ConciergeAgent();
        const calendarId = process.env.GHL_CALENDAR_ID || 'default_calendar';
        for (const lead of hotLeads) {
            console.log(`[Concierge] Engaging Lead: ${lead.email}`);
            // await concierge.handleBooking(lead, calendarId);
        }
    } else {
        console.log('No hot leads for concierge engagement.');
    }

    console.log('\n🚀 [OMNI-LOOP] CYCLE COMPLETE.');
}

runOmniLoop().catch(err => {
    console.error('Critical Loop Failure:', err);
});
