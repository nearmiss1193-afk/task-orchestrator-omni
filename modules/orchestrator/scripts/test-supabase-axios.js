const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function testDirect() {
    const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/leads?select=*`;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

    console.log(`Pinging: ${url}`);

    try {
        const response = await axios.get(url, {
            headers: {
                'apikey': key,
                'Authorization': `Bearer ${key}`
            }
        });

        console.log('Status:', response.status);
        console.log('Response:', JSON.stringify(response.data, null, 2));
    } catch (err) {
        console.error('Axios error:', err.message);
        if (err.response) {
            console.error('Response Status:', err.response.status);
            console.error('Response Data:', JSON.stringify(err.response.data, null, 2));
        }
    }
}

testDirect();
