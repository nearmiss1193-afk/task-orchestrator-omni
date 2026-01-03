const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function checkRestRoot() {
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;

    try {
        console.log(`Checking REST root: ${url}/rest/v1/`);
        const response = await axios.get(`${url}/rest/v1/`, {
            headers: {
                'apikey': key,
                'Authorization': `Bearer ${key}`
            }
        });
        console.log('✅ Connected!');
        console.log('Available Definitions:', Object.keys(response.data.definitions || {}));
    } catch (err) {
        console.error('REST Error:', err.response?.data?.message || err.message);
        if (err.response) {
            console.error('Full Error:', JSON.stringify(err.response.data, null, 2));
        }
    }
}

checkRestRoot();
