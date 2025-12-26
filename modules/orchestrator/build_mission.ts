
import axios from 'axios';
import dotenv from 'dotenv';
dotenv.config();

const API_URL = 'http://localhost:3004/api/agent/execute';

async function runBuild() {
    try {
        console.log("Triggering Profit System Build...");

        const response = await axios.post(API_URL, {
            planCallback: {
                id: `build-${Date.now()}`,
                originalGoal: "Build AI Service Profit System",
                status: "PENDING",
                steps: [
                    {
                        id: "step_build_1",
                        connectorName: "GHL_Browser",
                        action: "create_funnel_page",
                        params: {
                            name: "AI Service Profit System"
                        },
                        status: "PENDING",
                        attempts: 0
                    }
                ],
                createdAt: new Date().toISOString()
            }
        });

        console.log("Build Mission Started:", response.data);
        const fs = require('fs');
        fs.writeFileSync('build_response.json', JSON.stringify(response.data, null, 2));
    } catch (error: any) {
        console.error("Failed to trigger build:", error.message);
        if (error.response) console.error(error.response.data);
    }
}

runBuild();
