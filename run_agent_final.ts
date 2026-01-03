
import path from 'path';
import fs from 'fs';

const libPath = path.resolve(__dirname, 'modules/orchestrator/lib/marketing-agent.ts');
console.log("Checking path:", libPath);

if (!fs.existsSync(libPath)) {
    console.error("❌ FILE NOT FOUND AT:", libPath);
    process.exit(1);
}

// Dynamic Import
import(libPath).then(async (module) => {
    console.log("🛠️ Module Loaded. Initializing...");
    const { MarketingAgent } = module;
    try {
        const agent = new MarketingAgent();
        await agent.start();
        console.log("✅ Marketing Agent Started Successfully.");
    } catch (e) {
        console.error("❌ AGENT LOGIC FAILURE:", e);
    }
}).catch(err => {
    console.error("❌ IMPORT FAILURE:", err);
});
