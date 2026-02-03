const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function verifyGHL() {
    console.log('--- VERIFYING GHL CONNECTION ---');
    const token = process.env.GHL_PRIVATE_KEY;
    const locationId = process.env.GHL_LOCATION_ID;

    if (!token || !locationId) {
        console.error('❌ Missing GHL credentials in .env.local');
        return;
    }

    try {
        const response = await axios.get('https://services.leadconnectorhq.com/forms/', {
            params: { locationId },
            headers: {
                'Authorization': `Bearer ${token}`,
                'Version': '2021-07-28'
            }
        });
        console.log('✅ GHL CONNECTION SUCCESSFUL!');
        console.log('Available Forms:', response.data.forms?.length || 0);
    } catch (e) {
        console.error('❌ GHL CONNECTION FAILED:', e.response?.data?.message || e.message);
        if (e.response) {
            console.error('Response:', JSON.stringify(e.response.data, null, 2));
        }
    }
}

verifyGHL();
