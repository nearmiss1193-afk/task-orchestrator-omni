
import axios from 'axios';

async function triggerAgent() {
    const instruction = "Build me a landing page complete with contact payment widget embeds in my funnels section, find leads from plumbers in Florida, email them, and report performance.";

    console.log("Triggering Agent on localhost:3002...");
    try {
        const response = await axios.post('http://localhost:3004/api/agent/plan', {
            instruction: instruction
        });
        const plan = response.data;
        console.log("Plan Generated. ID:", plan.id);

        console.log("Executing Plan...");
        const execResponse = await axios.post('http://localhost:3004/api/agent/execute', {
            planId: plan.id
        });
        console.log("Execution Started:", execResponse.data);

    } catch (error: any) {
        console.error("Error triggering agent:", error.message);
        if (error.response) {
            console.error("Status:", error.response.status);
            console.error("Data:", error.response.data);
        }
    }
}

triggerAgent();
