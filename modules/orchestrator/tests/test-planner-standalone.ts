
import { Planner } from '../lib/planner';
import * as dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });

async function testPlanner() {
    const planner = new Planner();
    const userInput = "Email hello@example.com with a welcome message and search for leads in Florida.";
    console.log(`Testing Planner with: "${userInput}"`);
    try {
        const plan = await planner.generatePlan(userInput);
        console.log("Generated Plan:");
        console.log(JSON.stringify(plan, null, 2));
    } catch (error: any) {
        console.error("Planner Test Failed:");
        console.error(error.stack || error.message || error);
        if (error.response) {
            console.error("Error Response Data:", JSON.stringify(error.response.data, null, 2));
        }
    }
}

testPlanner();
