
import { Planner } from '../lib/planner';
import { Orchestrator } from '../lib/orchestrator';
import { StateManager } from '../lib/state-manager';
require('dotenv').config({ path: '.env.local' }); // Load env for test

async function runTest() {
    console.log("--- Starting Agentic Orchestrator Test (With Claude) ---");

    // 1. Plan
    console.log("\n[1] Generating Plan with Claude...");
    const planner = new Planner();
    const instruction = "Build a website for my AI Service Co leads from Zillow plumbers in Orlando, email them with our AI missed call offer, schedule 7 Facebook posts, and report performance.";

    try {
        const plan = await planner.generatePlan(instruction);
        console.log(`Plan Generated: ${plan.id} with ${plan.steps.length} steps.`);

        // Basic validation of plan quality from LLM
        if (plan.steps.length === 0) {
            console.error("FAILED: Plan has 0 steps.");
            process.exit(1);
        }
        const hasZillow = plan.steps.some(s => s.connectorName === 'Zillow');
        const hasFB = plan.steps.some(s => s.connectorName === 'Facebook');

        if (!hasZillow || !hasFB) {
            console.warn("WARNING: Plan might be missing connectors. check steps:", plan.steps);
        }

        // Save Setup
        StateManager.savePlan(plan);

        // 2. Execute
        console.log("\n[2] Executing Plan...");
        const orchestrator = new Orchestrator();

        const executionPromise = orchestrator.executePlan(plan.id);

        const poller = setInterval(() => {
            const current = StateManager.getPlan(plan.id);
            if (!current) return;

            const completed = current.steps.filter(s => s.status === 'COMPLETED').length;
            const pending = current.steps.filter(s => s.status === 'PENDING').length;
            const running = current.steps.filter(s => s.status === 'RUNNING').length;

            process.stdout.write(`\rStatus: ${current.status} | Completed: ${completed}/${current.steps.length} | Pending: ${pending} | Running: ${running}  `);

            if (current.status === 'COMPLETED' || current.status === 'FAILED') {
                clearInterval(poller);
            }
        }, 500);

        await executionPromise;
        console.log("\n\nExecution Finished.");

        // 3. Verify
        const finalPlan = StateManager.getPlan(plan.id);
        const logs = StateManager.getLogs(plan.id);

        console.log(`\n[3] Final Status: ${finalPlan?.status}`);
        console.log(`Total Logs generated: ${logs.length}`);

        if (finalPlan?.status === 'COMPLETED') {
            console.log("\n✅ SUCCESS: All steps completed.");
            process.exit(0);
        } else {
            console.error("\n❌ FAILED: Plan did not complete successfully.");
            process.exit(1);
        }
    } catch (err: any) {
        console.error("\n❌ FAILED during planning or execution:", err.message);
        process.exit(1);
    }
}

runTest().catch(e => console.error(e));
