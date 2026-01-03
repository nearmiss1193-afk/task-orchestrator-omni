const dotenv = require('dotenv');
// Load env vars immediately
dotenv.config({ path: '.env.local' });
// Enable TS support for requiring .ts files
require('ts-node').register({
    transpileOnly: true,
    project: 'tsconfig.test.json'
});

const { Orchestrator } = require('./lib/orchestrator');
const { Planner } = require('./lib/planner');
const { StateManager } = require('./lib/state-manager');

async function runLiveMission() {
    console.log("🚀 STARTING LIVE MISSION: SYSTEM BACKUP & NOTIFICATION");
    console.log("-----------------------------------------------------");

    // Verify Env Loaded
    if (!process.env.GHL_LOCATION_ID) {
        console.error("❌ ERROR: GHL_LOCATION_ID not found in env. Aborting.");
        process.exit(1);
    }
    console.log(`[Init] Env Loaded. Location ID: ${process.env.GHL_LOCATION_ID}`);

    const planner = new Planner();
    const orchestrator = new Orchestrator();

    // 1. Generate Plan
    const missionPrompt = "Scan my GHL account for funnels and forms, generate a performance report, and email the results to admin@example.com";
    console.log(`\n🗣️ User Request: "${missionPrompt}"\n`);

    console.log("🧠 Planner: Analyzing request with Gemini 1.5 Pro...");
    const plan = await planner.generatePlan(missionPrompt);

    console.log(`\n📋 Plan Generated (ID: ${plan.id}):`);
    plan.steps.forEach(s => console.log(`   [${s.id}] ${s.connectorName} -> ${s.action}`));

    // Save initial state
    StateManager.savePlan(plan);

    // 2. Execute Plan
    console.log("\n⚙️ Orchestrator: Beginning Execution...\n");
    await orchestrator.executePlan(plan.id);

    // 3. Final Report
    const finalState = StateManager.getPlan(plan.id);
    if (!finalState) return;

    console.log("\n-----------------------------------------------------");
    console.log(`🏁 Mission Status: ${finalState.status}`);
    console.log("-----------------------------------------------------");

    if (finalState.status === 'COMPLETED') {
        console.log("✅ SUCCESS! Backup completed and Admin notified.");
        process.exit(0);
    } else {
        console.log("❌ MISSION FAILED. Check logs.");
        process.exit(1);
    }
}

runLiveMission();
