
import { GHLConnector } from '../lib/connectors/ghl';
import * as dotenv from 'dotenv';
import * as path from 'path';

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

async function testGHLOutreach() {
    const ghl = new GHLConnector();
    const testEmail = "nearmiss1193@gmail.com";
    const testPhone = "+13529368152";

    console.log(`🧪 Testing GHL Send to ${testEmail}...`);

    try {
        // 1. Resolve Contact
        const contactId = await (ghl as any).resolveContact(testEmail);
        console.log(`Resolved Contact ID: ${contactId}`);

        // 2. Send SMS
        console.log("Sending Test SMS...");
        const smsRes = await ghl.execute('send_sms', {
            contactId,
            body: "🚀 [System Check] Outreach SMS is functional. Turbo Mode Active."
        });
        console.log("SMS Result:", smsRes);

        // 3. Send Email
        console.log("Sending Test Email...");
        const emailRes = await ghl.execute('send_email', {
            contactId,
            subject: "🚀 System Outreach Verified",
            body: "The AI system is now successfully dispatching both SMS and Email assets."
        });
        console.log("Email Result:", emailRes);

        console.log("✅ GHL Outreach Test Complete.");

    } catch (e: any) {
        console.error("❌ Outreach Test Failed:", e.message);
    }
}

testGHLOutreach();
