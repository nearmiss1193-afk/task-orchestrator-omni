const fetch = require('node-fetch');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function testDirect() {
    const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/leads?select=*`;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

    console.log(`Pinging: ${url}`);

    try {
        const response = await fetch(url, {
            headers: {
                'apikey': key,
                'Authorization': `Bearer ${key}`
            }
        });

        const data = await response.json();
        console.log('Status:', response.status);
        console.log('Response:', JSON.stringify(data, null, 2));
    } catch (err) {
        console.error('Fetch error:', err.message);
    }
}

testDirect();
