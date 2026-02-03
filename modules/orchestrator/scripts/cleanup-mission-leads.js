const { createClient } = require('@supabase/supabase-js');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

async function cleanup() {
    console.log('Cleaning up Mission: First Strike leads...');
    const { error } = await supabase
        .from('contacts_master')
        .delete()
        .ilike('ghl_contact_id', 'mission_fs_%');

    if (error) {
        console.error('Error during cleanup:', error);
    } else {
        console.log('Cleanup successful.');
    }
}

cleanup();
