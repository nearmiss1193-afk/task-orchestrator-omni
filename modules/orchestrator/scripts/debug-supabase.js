const { createClient } = require('@supabase/supabase-js');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

async function checkSchema() {
    console.log('--- CHECKING SUPABASE SCHEMA ---');
    try {
        // Try a raw RPC or a meta-query if possible, 
        // but since we don't have RPCs set up, let's try to query the information_schema via a trick or just catching specific errors.

        const { data, error } = await supabase
            .from('leads')
            .select('*')
            .limit(1);

        if (error) {
            console.log('Error querying leads table:', error.message);
            console.log('Full error object:', JSON.stringify(error, null, 2));
        } else {
            console.log('Success! Leads table found.');
        }

        // Try to query another table just in case
        const { data: data2, error: error2 } = await supabase
            .from('todos')
            .select('*')
            .limit(1);

        if (error2) {
            console.log('Error querying todos table:', error2.message);
        } else {
            console.log('Success! Todos table found.');
        }

    } catch (err) {
        console.error('Unexpected error:', err);
    }
}

checkSchema();
