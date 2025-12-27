
import { MarketingAgent } from '../lib/marketing-agent';

console.log("🛠️ Initializing Marketing Agent via Direct Script...");
async function run() {
    try {
        const agent = new MarketingAgent();
        await agent.start();
        console.log("✅ Marketing Agent Started Successfully.");
    } catch (e) {
        console.error("❌ CRITICAL FAILURE:", e);
    }
}
run();
