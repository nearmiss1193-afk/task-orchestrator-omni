require('dotenv').config({ path: '.env.local' });
const { GoogleGenerativeAI } = require('@google/generative-ai');

async function testPro() {
    console.log("TESTING GEMINI-PRO (1.0)...");
    try {
        const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
        const model = genAI.getGenerativeModel({ model: "gemini-pro" });
        const res = await model.generateContent("Say 'ONLINE'");
        console.log(`RESULT: ${res.response.text()}`);
    } catch (e) {
        console.log(`ERROR: ${e.message}`);
    }
}
testPro();
