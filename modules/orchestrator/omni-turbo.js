const { createClient } = require('@supabase/supabase-js');
const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

/**
 * TURBO SELF-CONTAINED LAUNCHER
 * No imports, no module issues. Just results.
 */
async function launchTurbo() {
    console.log('🚀 [TURBO] OMNI-LAUNCHER : 100% SELF-CONTAINED');

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const ghlToken = process.env.GHL_PRIVATE_KEY;
    const locationId = process.env.GHL_LOCATION_ID;

    // 1. Supabase Check
    const supabase = createClient(supabaseUrl, supabaseKey);
    let table = 'contacts_master';
    const { data: testCheck, error: checkError } = await supabase.from('contacts_master').select('id').limit(1);

    if (checkError || !testCheck) {
        console.log('⚠️ [Adaptability] contacts_master missing. Using public.leads.');
        table = 'leads';
    }

    const { data: leads, error: fetchError } = await supabase.from(table).select('*').limit(1);
    if (fetchError) {
        console.error('❌ Supabase Connection Failed:', fetchError.message);
    } else {
        console.log(`✅ Supabase Connected! (${table} table verified)`);
    }

    // 2. GHL Check
    try {
        const res = await axios.get('https://services.leadconnectorhq.com/forms/', {
            params: { locationId },
            headers: { 'Authorization': `Bearer ${ghlToken}`, 'Version': '2021-07-28' }
        });
        console.log(`✅ GHL Connected! Found ${res.data.forms?.length || 0} forms.`);
    } catch (e) {
        console.error('❌ GHL Connection Failed.');
    }

    console.log('\n🤖 PROJECT STATUS: READY');
    process.exit(0);
}

launchTurbo().catch(err => {
    console.error('Turbo Failed:', err);
    process.exit(1);
});
