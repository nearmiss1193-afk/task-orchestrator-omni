require('dotenv').config({ path: '.env.local' });
const { GoogleGenerativeAI } = require('@google/generative-ai');

async function testFlash() {
    console.log("TESTING GEMINI-1.5-FLASH...");
    const key = process.env.GOOGLE_API_KEY;
    if (!key || key.startsWith("TODO")) {
        console.log("INVALID KEY DETECTED IN ENV");
        return;
    }
    try {
        const genAI = new GoogleGenerativeAI(key);
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
        const res = await model.generateContent("Hello");
        console.log(`RESULT: ${res.response.text()}`);
    } catch (e) {
        console.log(`ERROR: ${e.message}`);
    }
}
testFlash();
