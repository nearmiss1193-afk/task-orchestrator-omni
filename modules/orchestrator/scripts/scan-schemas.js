const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function scanSchemas() {
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const schemas = ['public', 'api', 'anitgravity'];

    for (const schema of schemas) {
        const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/leads?select=*`;
        console.log(`Checking schema '${schema}' at: ${url}`);

        try {
            const response = await axios.get(url, {
                headers: {
                    'apikey': key,
                    'Authorization': `Bearer ${key}`,
                    'Accept-Profile': schema // This tells PostgREST which schema to use
                }
            });

            console.log(`✅ FOUND in schema '${schema}'! Status:`, response.status);
            console.log('Sample Data:', response.data);
            return;
        } catch (err) {
            console.log(`❌ Not in '${schema}':`, err.response?.data?.message || err.message);
        }
    }

    // Also try querying 'anitgravity' table in 'public'
    try {
        const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/anitgravity?select=*`;
        const response = await axios.get(url, {
            headers: { 'apikey': key, 'Authorization': `Bearer ${key}` }
        });
        console.log(`✅ FOUND table 'anitgravity' in public schema!`);
    } catch (err) {
        console.log(`❌ Table 'anitgravity' not found in public.`);
    }
}

scanSchemas();
