import { Orchestrator } from '../lib/orchestrator';
import { Plan } from '../lib/types';
import { StateManager } from '../lib/state-manager';
import * as dotenv from 'dotenv';
import * as path from 'path';

dotenv.config({ path: path.resolve(__dirname, '../.env.local') });

async function runRealLifeMission() {
    console.log("🚀 STARTING REAL-LIFE ONBOARDING MISSION...");

    const orchestrator = new Orchestrator();

    const plan: Plan = {
        id: 'real-life-mission-' + Date.now(),
        originalGoal: "Fix funnel logic and test real onboarding flow",
        createdAt: new Date().toISOString(),
        status: 'PENDING',
        steps: [
            {
                id: 'step_1',
                connectorName: 'GHL_Browser',
                action: 'create_funnel_page',
                params: { name: 'Real-Life Onboarding Funnel ' + new Date().toISOString().split('T')[0] },
                status: 'PENDING',
                attempts: 0
            },
            {
                id: 'step_2',
                connectorName: 'GHL',
                action: 'upsert_contact',
                params: {
                    email: 'nearmiss1193@gmail.com',
                    firstName: 'User',
                    lastName: 'Test',
                    phone: '+15555555555'
                },
                status: 'PENDING',
                dependsOn: ['step_1'],
                attempts: 0
            },
            {
                id: 'step_3',
                connectorName: 'GHL',
                action: 'send_email',
                params: {
                    to: 'nearmiss1193@gmail.com',
                    subject: 'Welcome to your new Funnel',
                    body: 'Your funnel is ready at: {{step_1.result.funnelName}}. Go to onboarding now!'
                },
                status: 'PENDING',
                dependsOn: ['step_1', 'step_2'],
                attempts: 0
            }
        ]
    };

    StateManager.savePlan(plan);
    console.log(`Plan Saved: ${plan.id}. Executing...`);

    await orchestrator.executePlan(plan.id);

    const finalPlan = StateManager.getPlan(plan.id);
    console.log("\nMISSION RESULT:", finalPlan?.status);
    console.log("STEPS:", JSON.stringify(finalPlan?.steps, null, 2));
}

runRealLifeMission().catch(err => {
    console.error("❌ Mission Failed:", err);
});
