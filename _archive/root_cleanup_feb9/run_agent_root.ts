
import { MarketingAgent } from './modules/orchestrator/lib/marketing-agent.ts';

console.log("🛠️ Initializing Marketing Agent via Root Script...");
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
