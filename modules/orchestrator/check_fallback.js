require('dotenv').config({ path: '.env.local' });
const { GoogleGenerativeAI } = require('@google/generative-ai');

async function checkStandardModels() {
    const key = process.env.GOOGLE_API_KEY;
    if (!key) { console.log("No Key"); return; }

    const genAI = new GoogleGenerativeAI(key);

    const candidates = ["gemini-pro", "gemini-1.5-flash", "gemini-1.5-pro-latest"];

    for (const m of candidates) {
        process.stdout.write(`Testing ${m}... `);
        try {
            const model = genAI.getGenerativeModel({ model: m });
            await model.generateContent("Hi");
            console.log("✅ OK");
        } catch (e) {
            console.log(`❌ FAIL (${e.status || e.message})`);
        }
    }
}
checkStandardModels();
