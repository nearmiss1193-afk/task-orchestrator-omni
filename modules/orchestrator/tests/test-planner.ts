
require('dotenv').config({ path: '.env.local' });
import { Planner } from '../lib/planner';

async function testPlanner() {
    console.log("Testing Planner with API Key:", process.env.ANTHROPIC_API_KEY ? "Found" : "Missing");

    const planner = new Planner();
    try {
        console.log("Sending request to Claude...");
        const plan = await planner.generatePlan("Build a website for my AI Service Co leads from Zillow plumbers in Orlando");
        console.log("Plan generated successfully:", JSON.stringify(plan, null, 2));
    } catch (error: any) {
        console.error("Planner Error:", error);
        if (error.response) {
            console.error("API Response:", error.response.data);
        }
    }
}

testPlanner();
