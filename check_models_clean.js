require('dotenv').config({ path: '.env.local' });
const { GoogleGenerativeAI } = require('@google/generative-ai');

async function listModels() {
    const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
    try {
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro" });
        console.log("Checking model access...");
        // There isn't a simple "listModels" on the instance in all SDK versions,
        // but let's try to just output what we have or print a success if 1.5 works.
        // Actually, let's use the API to get the model list if possible, or just default to knowns.

        // Use REST for listing if SDK doesn't expose it easily in this version
        // But for now, let's just test 1.5 Pro and 1.5 Flash explicitly.

        const modelsToTest = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro", "gemini-pro", "gemini-ultras", "gemini-3.0-pro"];

        for (const m of modelsToTest) {
            try {
                const mod = genAI.getGenerativeModel({ model: m });
                const res = await mod.generateContent("Test");
                if (res && res.response) {
                    console.log(`✅ AVAILABLE: ${m}`);
                }
            } catch (e) {
                console.log(`❌ UNAVAILABLE: ${m} (${e.message.split(' ')[0]}...)`);
            }
        }

    } catch (error) {
        console.error("Error:", error);
    }
}
listModels();
