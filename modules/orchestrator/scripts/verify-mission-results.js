const { createClient } = require('@supabase/supabase-js');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.error('Missing Supabase credentials');
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function verifyResults() {
    console.log('--- MISSION: FIRST STRIKE RESULTS AUDIT ---');
    const { data, error } = await supabase
        .from('contacts_master')
        .select('full_name, website_url, ai_strategy, lead_score, status')
        .ilike('ghl_contact_id', 'mission_fs_%')
        .order('ghl_contact_id');

    if (error) {
        console.error('Error fetching results:', error);
        return;
    }

    if (!data || data.length === 0) {
        console.log('No results found for Mission: First Strike leads.');
        return;
    }

    data.forEach((lead, index) => {
        console.log(`\nLEAD #${index + 1}: ${lead.full_name}`);
        console.log(`URL: ${lead.website_url}`);
        console.log(`STATUS: ${lead.status}`);
        console.log(`SCORE: ${lead.lead_score}`);
        console.log(`HOOK: ${lead.ai_strategy || 'PENDING...'}`);
    });

    const enriched = data.filter(l => l.status === 'research_done').length;
    console.log(`\nOVERALL PROGRESS: ${enriched}/${data.length} Leads Enriched.`);
}

verifyResults();
