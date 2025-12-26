
require('dotenv').config({ path: '.env.local' });
import { GHLConnector } from '../lib/connectors/ghl';
import * as fs from 'fs';

async function testEmail() {
    console.log("Testing Email Connector...");
    console.log("User:", process.env.ADMIN_EMAIL);

    // Safety check mostly for logging (masks password)
    console.log("Pass:", process.env.ADMIN_PASSWORD ? "****" : "MISSING");

    const email = new GHLConnector();
    try {
        const res = await email.execute('send_email', {
            to: process.env.ADMIN_EMAIL, // Send to self
            subject: 'Agentic Test Email',
            body: 'This is a test from your Local Agentic Orchestrator.'
        });
        console.log("Success:", res);
    } catch (e: any) {
        console.error("Failed:", e.message);
        const errorLog = {
            message: e.message,
            stack: e.stack,
            response: e.response ? {
                status: e.response.status,
                data: e.response.data,
                headers: e.response.headers
            } : 'No response data'
        };
        fs.writeFileSync('error.log', JSON.stringify(errorLog, null, 2));
    }
}

testEmail();
