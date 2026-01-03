const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function getOpenApi() {
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/`;

    try {
        const response = await axios.get(url, {
            headers: {
                'apikey': key,
                'Authorization': `Bearer ${key}`
            }
        });

        console.log('✅ Connected to OpenAPI root!');
        if (response.data.definitions) {
            console.log('Exposed Tables:', Object.keys(response.data.definitions));
        } else if (response.data.paths) {
            console.log('Exposed Paths:', Object.keys(response.data.paths));
        } else {
            console.log('Response content:', JSON.stringify(response.data).substring(0, 500));
        }
    } catch (err) {
        console.error('Error fetching root:', err.response?.data?.message || err.message);
    }
}

getOpenApi();
