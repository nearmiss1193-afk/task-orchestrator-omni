
require('dotenv').config({ path: '.env.local' });
import { MarketingAgent } from '../lib/marketing-agent';

async function run() {
    console.log("🛠️ Initializing Marketing Agent...");
    const agent = new MarketingAgent();
    await agent.start();

    console.log("✅ Marketing Agent is running in the background.");
    console.log("Waiting for new leads in Supabase...");

    // Keep process alive
    process.stdin.resume();
}

run().catch(err => {
    console.error("❌ Agent failed to start:", err);
    process.exit(1);
});
