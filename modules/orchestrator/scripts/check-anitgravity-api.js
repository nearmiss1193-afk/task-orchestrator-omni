const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function checkAnitgravityApi() {
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/anitgravity?select=*`;

    console.log(`Checking 'anitgravity' in schema 'api'...`);

    try {
        const response = await axios.get(url, {
            headers: {
                'apikey': key,
                'Authorization': `Bearer ${key}`,
                'Accept-Profile': 'api'
            }
        });

        console.log(`✅ FOUND! Data:`, response.data);
    } catch (err) {
        console.error('❌ FAILED:', err.response?.data?.message || err.message);
    }
}

checkAnitgravityApi();
