
// Direct TS execution
import { MarketingAgent } from './modules/orchestrator/lib/marketing-agent';

async function run() {
    console.log("🛠️ Initializing Marketing Agent...");
    try {
        const agent = new MarketingAgent();
        await agent.start();
        console.log("✅ Marketing Agent Started.");
    } catch (e) {
        console.error("CRITICAL AGENT FAILURE:", e);
    }
}
run();
