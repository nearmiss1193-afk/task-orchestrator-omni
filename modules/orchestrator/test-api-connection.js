
const axios = require('axios');

async function testApi() {
    try {
        console.log("Testing http://localhost:3000/api/agent/plan");
        const res = await axios.post('http://localhost:3000/api/agent/plan', {
            instruction: "Build a funnel page for my AI Service Co leads from Zillow plumbers in Orlando, email them with our AI missed call offer, schedule 7 Facebook posts, and report performance."
        });
        console.log("Success:", res.data);
    } catch (error) {
        if (error.response) {
            console.error("Server Error:", error.response.status, error.response.data);
        } else {
            console.error("Connection Error (Server might not be running on 3000):", error.message);
        }
    }
}

testApi();
