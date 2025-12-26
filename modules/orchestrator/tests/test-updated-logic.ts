require('dotenv').config({ path: '.env.local' });
import { Planner } from '../lib/planner';

async function testPlannerLogic() {
    const planner = new Planner();

    console.log("Testing Planner with 'Backup' Request...");
    const prompt = "Audit my GHL account to get a count of funnels and then send a backup notification to admin@example.com";

    try {
        const plan = await planner.generatePlan(prompt);
        console.log("Plan Generated:");
        console.log(JSON.stringify(plan, null, 2));

        // Validation Logic
        const auditStep = plan.steps.find(s => s.action === 'audit_account');
        const emailStep = plan.steps.find(s => s.action === 'send_email');

        if (!auditStep) console.error("FAILED: Missing audit step");
        if (!emailStep) console.error("FAILED: Missing email step");

        if (emailStep) {
            if (emailStep.connectorName === 'Email') {
                console.log("SUCCESS: Planner correctly chose 'Email' connector for admin notification.");
            } else {
                console.error(`FAILED: Planner chose '${emailStep.connectorName}' for admin notification (Expected 'Email').`);
            }
        }
    } catch (e) {
        console.error("Planner Error:", e);
    }
}

testPlannerLogic();
