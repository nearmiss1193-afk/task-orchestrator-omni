const { createClient } = require('@supabase/supabase-js');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
    console.error('Missing Supabase credentials in .env.local');
    process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

async function createTestLead() {
    console.log('--- CREATING TEST LEAD (JS) ---');

    const testLead = {
        email: 'test@example.com',
        website_url: 'https://example.com',
        status: 'new'
    };

    try {
        // First delete if exists to ensure a fresh test
        await supabase.from('leads').delete().eq('email', testLead.email);

        const { data, error } = await supabase
            .from('leads')
            .insert([testLead])
            .select();

        if (error) throw error;

        console.log('[SUCCESS] Test lead created/reset:', data);
    } catch (error) {
        console.error('Failed to create test lead:', error.message);
    }
}

createTestLead();
