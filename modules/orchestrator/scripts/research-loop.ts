import * as dotenv from 'dotenv';
import * as path from 'path';
import { supabase } from '../lib/supabase';
import { ResearchAgent } from '../lib/research-agent';

// Load environment variables from .env.local
dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function runResearchLoop() {
    console.log('--- STARTING RESEARCH LOOP ---');
    const agent = new ResearchAgent();

    try {
        // 1. Fetch leads that are 'new' or have no copy
        const { data: leads, error } = await supabase
            .from('leads')
            .select('*')
            .or('status.eq.new,personalized_copy.is.null');

        if (error) throw error;

        if (!leads || leads.length === 0) {
            console.log('No new leads found. Sleeping...');
            return;
        }

        console.log(`Found ${leads.length} new leads to process.`);

        for (const lead of leads) {
            console.log(`\nProcessing Lead: ${lead.email}`);

            if (!lead.website_url) {
                console.log(`Skipping ${lead.email}: No website URL.`);
                continue;
            }

            // 2. Scrape website
            const websiteText = await agent.scrapeWebsite(lead.website_url);

            if (!websiteText) {
                console.log(`Skipping ${lead.email}: Could not extract text from website.`);
                await supabase
                    .from('leads')
                    .update({ personalized_copy: 'MANUAL REVIEW REQUIRED: Website unreachable or no text found.' })
                    .eq('id', lead.id);
                continue;
            }

            // 3. Generate Proposal
            const proposal = await agent.generateProposal(websiteText);

            // 4. Update Supabase with copy and status
            const { error: updateError } = await supabase
                .from('leads')
                .update({
                    personalized_copy: proposal,
                    status: 'ready_to_send'
                })
                .eq('id', lead.id);

            if (updateError) {
                console.error(`Failed to update ${lead.email}:`, updateError.message);
            } else {
                console.log(`[SUCCESS] Personalized copy generated for ${lead.email}`);
            }
        }

    } catch (error: any) {
        console.error('CRITICAL ERROR in research loop:', error.message);
    }

    console.log('--- RESEARCH LOOP COMPLETED ---');
}

// Run the loop once (can be scheduled with cron or while(true) loop)
runResearchLoop();
