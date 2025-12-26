const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function getApiSchemaSpec() {
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    const url = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/`;

    try {
        const response = await axios.get(url, {
            headers: {
                'apikey': key,
                'Authorization': `Bearer ${key}`,
                'Accept-Profile': 'api'
            }
        });

        console.log('✅ Connected to API schema root!');
        if (response.data.definitions) {
            console.log('Exposed Tables in api:', Object.keys(response.data.definitions));
        } else {
            console.log('Definitions missing. Paths:', Object.keys(response.data.paths || {}));
        }
    } catch (err) {
        console.error('Error:', err.response?.data?.message || err.message);
    }
}

getApiSchemaSpec();
