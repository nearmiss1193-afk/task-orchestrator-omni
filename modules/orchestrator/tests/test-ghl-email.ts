
require('dotenv').config({ path: '.env.local' });
import { GHLConnector } from '../lib/connectors/ghl';

async function testGHLEmail() {
    console.log("Testing GHL Email Sending...");
    const ghl = new GHLConnector();

    // Test Email
    const email = process.env.ADMIN_EMAIL || 'test@example.com';
    try {
        console.log(`Sending GHL Email to ${email}...`);
        const res = await ghl.execute('send_email', {
            to: email,
            subject: 'GHL Test',
            body: 'This email was sent via GoHighLevel API from the Agentic System.'
        });
        console.log("Email Result:", res);
    } catch (e: any) {
        console.error("Email Failed:", e.message);
        if (e.response) console.error(e.response.data);
    }
}

testGHLEmail();
