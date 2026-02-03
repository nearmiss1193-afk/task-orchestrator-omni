
require('dotenv').config({ path: '.env.local' });
import { Planner } from '../lib/planner';

async function testGeminiPlanner() {
    console.log("Testing Gemini Planner...");
    const planner = new Planner();

    const instruction = "Scrape 5 leads from Zillow for plumbers in Miami, then send them an email via GHL with the subject 'Partnership Opportunity' and a body inviting them to join our network.";

    try {
        console.log(`Input Instruction: "${instruction}"`);
        const plan = await planner.generatePlan(instruction);

        console.log("\n--- Generated Plan ---");
        console.log(JSON.stringify(plan, null, 2));

        if (plan.steps.length > 0 && plan.steps[0].connectorName !== 'GHL' || plan.steps.some(s => s.connectorName === 'GoogleMaps' || s.connectorName === 'Zillow')) {
            console.log("\nSuccess: Plan contains expected steps.");
        } else {
            console.log("\nWarning: Plan might be a fallback or contains unexpected steps.");
        }

    } catch (error) {
        console.error("Test Failed:", error);
    }
}

testGeminiPlanner();
