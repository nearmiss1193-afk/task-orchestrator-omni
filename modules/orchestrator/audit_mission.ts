
import axios from 'axios';
import dotenv from 'dotenv';
dotenv.config();

const API_URL = 'http://localhost:3004/api/agent/execute'; // Ensure URL is correct

async function runAudit() {
    try {
        console.log("Triggering Account Audit...");

        // Direct Plan Injection to bypass Planner (faster/safer for this specific task)
        const response = await axios.post(API_URL, {
            planCallback: {
                id: `audit-${Date.now()}`,
                originalGoal: "Audit GHL Account",
                status: "PENDING",
                steps: [
                    {
                        id: "step_verification_1",
                        connectorName: "GHL_Browser",
                        action: "audit_account",
                        params: {},
                        status: "PENDING",
                        attempts: 0
                    }
                ],
                createdAt: new Date().toISOString()
            }
        });

        console.log("Audit Mission Started:", response.data);
        const fs = require('fs');
        fs.writeFileSync('audit_response.json', JSON.stringify(response.data, null, 2));
    } catch (error: any) {
        console.error("Failed to trigger audit:", error.message);
        if (error.response) console.error(error.response.data);
    }
}

runAudit();
