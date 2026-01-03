const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function manualInsert() {
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/leads`;

    console.log(`Attempting manual insert into 'api.leads'...`);

    try {
        const response = await axios.post(url, {
            email: 'manual-test@example.com',
            website_url: 'https://example.com',
            status: 'new'
        }, {
            headers: {
                'apikey': key,
                'Authorization': `Bearer ${key}`,
                'Content-Type': 'application/json',
                'Prefer': 'return=representation',
                'Content-Profile': 'api', // For POSTing to a different schema
                'Accept-Profile': 'api'    // For the response
            }
        });

        console.log('✅ SUCCESS! Inserted data:', response.data);
    } catch (err) {
        console.error('❌ FAILED:', err.response?.data?.message || err.message);
        if (err.response) {
            console.error('Full Error:', JSON.stringify(err.response.data, null, 2));
        }
    }
}

manualInsert();
