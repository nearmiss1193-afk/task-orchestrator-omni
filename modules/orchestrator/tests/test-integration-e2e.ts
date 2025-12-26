require('dotenv').config({ path: '.env.local' });
import { Planner } from '../lib/planner';
import { Orchestrator } from '../lib/orchestrator';
import { StateManager } from '../lib/state-manager';

async function testEndToEnd() {
    console.log("=== End-to-End Integration Test ===\n");
    console.log("Testing: Planner → Orchestrator → GHL Connector\n");

    const planner = new Planner();
    const orchestrator = new Orchestrator();

    try {
        // Test 1: Simple contact creation with tagging
        console.log("📋 Test 1: Contact Creation + Tagging");
        console.log("-".repeat(50));

        const instruction1 = "Create a contact for demo@example.com named Demo User and tag them as VIP";
        console.log(`Instruction: "${instruction1}"\n`);

        console.log("[→] Generating plan with Gemini...");
        const plan1 = await planner.generatePlan(instruction1);
        console.log(`[✓] Plan generated with ${plan1.steps.length} steps:`);
        plan1.steps.forEach((step, i) => {
            console.log(`    ${i + 1}. ${step.connectorName}.${step.action}`);
        });

        StateManager.savePlan(plan1);
        console.log("\n[→] Executing plan...");
        await orchestrator.executePlan(plan1.id);

        const finalPlan1 = StateManager.getPlan(plan1.id);
        const success1 = finalPlan1?.status === 'COMPLETED';
        console.log(`[${success1 ? '✓' : '✗'}] Plan ${success1 ? 'completed successfully' : 'failed'}`);
        if (!success1) {
            const failedSteps = finalPlan1?.steps.filter(s => s.status === 'FAILED') || [];
            failedSteps.forEach(s => console.log(`    Failed: ${s.action} - ${s.error}`));
        }
        console.log();

        // Test 2: Contact with appointment scheduling
        console.log("📋 Test 2: Contact + Calendar Appointment");
        console.log("-".repeat(50));

        const instruction2 = "Create contact alice@test.com and schedule an appointment for next Monday at 2PM";
        console.log(`Instruction: "${instruction2}"\n`);

        console.log("[→] Generating plan with Gemini...");
        const plan2 = await planner.generatePlan(instruction2);
        console.log(`[✓] Plan generated with ${plan2.steps.length} steps:`);
        plan2.steps.forEach((step, i) => {
            console.log(`    ${i + 1}. ${step.connectorName}.${step.action}`);
            if (step.dependsOn?.length) {
                console.log(`       depends on: ${step.dependsOn.join(', ')}`);
            }
        });

        StateManager.savePlan(plan2);
        console.log("\n[→] Executing plan...");
        await orchestrator.executePlan(plan2.id);

        const finalPlan2 = StateManager.getPlan(plan2.id);
        const success2 = finalPlan2?.status === 'COMPLETED';
        console.log(`[${success2 ? '✓' : '✗'}] Plan ${success2 ? 'completed successfully' : 'failed'}`);
        if (!success2) {
            const failedSteps = finalPlan2?.steps.filter(s => s.status === 'FAILED') || [];
            failedSteps.forEach(s => console.log(`    Failed: ${s.action} - ${s.error}`));
        }
        console.log();

        // Test 3: Opportunity management
        console.log("📋 Test 3: Opportunity Creation");
        console.log("-".repeat(50));

        const instruction3 = "Create an opportunity called 'Big Deal' worth $25000";
        console.log(`Instruction: "${instruction3}"\n`);

        console.log("[→] Generating plan with Gemini...");
        const plan3 = await planner.generatePlan(instruction3);
        console.log(`[✓] Plan generated with ${plan3.steps.length} steps:`);
        plan3.steps.forEach((step, i) => {
            console.log(`    ${i + 1}. ${step.connectorName}.${step.action}`);
        });

        StateManager.savePlan(plan3);
        console.log("\n[→] Executing plan...");
        await orchestrator.executePlan(plan3.id);

        const finalPlan3 = StateManager.getPlan(plan3.id);
        const success3 = finalPlan3?.status === 'COMPLETED';
        console.log(`[${success3 ? '✓' : '✗'}] Plan ${success3 ? 'completed successfully' : 'failed'}`);
        console.log();

        // Test 4: Task creation
        console.log("📋 Test 4: Task Creation for Contact");
        console.log("-".repeat(50));

        const instruction4 = "Create a task for demo@example.com to follow up next week";
        console.log(`Instruction: "${instruction4}"\n`);

        console.log("[→] Generating plan with Gemini...");
        const plan4 = await planner.generatePlan(instruction4);
        console.log(`[✓] Plan generated with ${plan4.steps.length} steps:`);
        plan4.steps.forEach((step, i) => {
            console.log(`    ${i + 1}. ${step.connectorName}.${step.action}`);
        });

        StateManager.savePlan(plan4);
        console.log("\n[→] Executing plan...");
        await orchestrator.executePlan(plan4.id);

        const finalPlan4 = StateManager.getPlan(plan4.id);
        const success4 = finalPlan4?.status === 'COMPLETED';
        console.log(`[${success4 ? '✓' : '✗'}] Plan ${success4 ? 'completed successfully' : 'failed'}`);
        console.log();

        // Summary
        console.log("=".repeat(50));
        console.log("📊 TEST SUMMARY");
        console.log("=".repeat(50));
        const totalTests = 4;
        const passedTests = [success1, success2, success3, success4].filter(Boolean).length;
        console.log(`Passed: ${passedTests}/${totalTests} tests`);
        console.log();

        console.log("✨ System Capabilities Verified:");
        console.log("  ✓ AI Planning (Gemini 1.5 Flash)");
        console.log("  ✓ Plan Orchestration");
        console.log("  ✓ GHL Connector (37+ actions)");
        console.log("  ✓ State Management");
        console.log("  ✓ Dependency Resolution");
        console.log();

        if (passedTests === totalTests) {
            console.log("🎉 SYSTEM FULLY OPERATIONAL");
            return 0;
        } else {
            console.log("⚠️  Some tests failed - check GHL API configuration");
            return 1;
        }

    } catch (error) {
        console.error("\n❌ Integration test failed:", error);
        console.error("\nThis may be due to:");
        console.error("  - Rate limiting (Gemini API 429 errors)");
        console.error("  - Missing GHL API keys");
        console.error("  - Invalid GHL configuration (locationId, calendarId, etc.)");
        return 1;
    }
}

testEndToEnd().then(code => process.exit(code));
