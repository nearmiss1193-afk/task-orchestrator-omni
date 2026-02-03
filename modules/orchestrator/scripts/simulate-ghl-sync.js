const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

/**
 * SIMULATE GHL SYNC
 * This script sends a mock GHL payload to our local webhook endpoint.
 */
async function simulateSync() {
    console.log('--- SIMULATING GHL SYNC EVENT ---');

    // In a real environment, you'd target your public URL. 
    // Locally, we target the dev server.
    const url = 'http://localhost:3000/api/webhook';

    const mockPayload = {
        id: 'contact_abc_123',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        phone: '+15550123456',
        website: 'https://johndoe.com',
        status: 'new',
        sentiment: 'positive',
        lead_score: 85
    };

    try {
        console.log('Sending mock payload to:', url);
        const response = await axios.post(url, mockPayload);
        console.log('✅ SYNC SUCCESSFUL!');
        console.log('Response:', JSON.stringify(response.data, null, 2));
    } catch (e) {
        console.error('❌ SYNC FAILED:', e.response?.data?.error || e.message);
        console.log('\n[Reminder] Ensure your local dev server is running (npm run dev) before running this script.');
    }
}

simulateSync();
