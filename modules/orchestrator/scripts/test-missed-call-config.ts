
import { GHLBrowserConnector } from '../lib/connectors/ghl-browser';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

async function testMissedCallOnboarding() {
    console.log("🧪 Testing Autonomous Missed Call Onboarding...");
    const browserAgent = new GHLBrowserConnector();

    try {
        const result = await browserAgent.execute('configure_missed_call', {
            message: "Hi, this is AI Service Co Service Bot. Sorry we missed your call. How can we help you today? ☎️"
        });

        console.log("Result:", result);
    } catch (e) {
        console.error("Test failed:", e);
    }
}

testMissedCallOnboarding().catch(console.error);
