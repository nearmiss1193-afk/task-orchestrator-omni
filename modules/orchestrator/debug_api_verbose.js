require('dotenv').config({ path: '.env.local' });
const { GoogleGenerativeAI } = require('@google/generative-ai');

async function debugAccess() {
    const key = process.env.GOOGLE_API_KEY;
    console.log(`Key present: ${!!key} (Length: ${key ? key.length : 0})`);

    if (!key) {
        console.error("❌ NO API KEY FOUND");
        return;
    }

    const genAI = new GoogleGenerativeAI(key);

    // Test generic model to check auth
    // Note: 'gemini-pro' is the most standard, stable alias.
    const models = ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro', 'gemini-1.0-pro'];

    for (const modelName of models) {
        console.log(`\nTesting: ${modelName}...`);
        try {
            const model = genAI.getGenerativeModel({ model: modelName });
            const result = await model.generateContent("Ping");
            const response = await result.response;
            console.log(`✅ SUCCESS: ${modelName} responded: "${response.text()}"`);
        } catch (error) {
            console.error(`❌ FAILED: ${modelName}`);
            console.error(`   Message: ${error.message}`);
            if (error.status) console.error(`   Status: ${error.status}`);
            if (error.statusText) console.error(`   StatusText: ${error.statusText}`);
            // If it's a 404, it means the model name is wrong or user doesn't have access.
            // If it's 403/400, it's auth/key.
        }
    }
}

debugAccess();
