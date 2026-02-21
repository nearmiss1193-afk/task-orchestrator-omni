import { NextResponse } from 'next/server';

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const { industry, companySize, primaryChallenge, currentCRM, email } = body;

        // In a live production environment, we would save this lead to GoHighLevel via Webhook here
        // fetch('https://services.leadconnectorhq.com/hooks/...', { method: 'POST', body: JSON.stringify(body) })

        console.log(`[LEAD CAPTURED] Assessment completed for ${email} in ${industry}`);

        // We construct a prompt for Gemini to dynamically grade the assessment
        const prompt = `You are an elite AI Automation Architect. A local service business owner just took our "AI Readiness Assessment".
        
        Business Data:
        - Industry: ${industry}
        - Primary Bottleneck: ${primaryChallenge}
        - Current CRM: ${currentCRM}
        
        Task:
        1. Give them an "AI Readiness Score" from 1-100 (Be realistic, usually 30-70 for local businesses).
        2. Write a 2-sentence analysis of their current operational bottleneck.
        3. Provide exactly 3 bullet points of specific AI workflows we (AI Service Co) should install for them.
        
        Return ONLY valid JSON in this exact format, with no markdown formatting or backticks:
        {
            "score": 45,
            "analysis": "Your business is...",
            "recommendations": ["Workflow 1", "Workflow 2", "Workflow 3"]
        }`;

        const geminiKey = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;

        if (!geminiKey) {
            // Fallback response if API key isn't configured in Vercel yet
            return NextResponse.json({
                score: 42,
                analysis: `Your ${industry} business is losing significant revenue to manual operations. Your current setup relying on ${currentCRM || 'manual entry'} is creating a severe bottleneck with ${primaryChallenge.toLowerCase()}.`,
                recommendations: [
                    "Deploy an AI Voice Receptionist to answer 24/7",
                    "Install our Speed-to-Lead SMS sequence",
                    "Activate an autonomous Database Reactivation campaign"
                ]
            });
        }

        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${geminiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }],
                generationConfig: { temperature: 0.2, response_mime_type: "application/json" }
            })
        });

        const data = await response.json();
        const jsonString = data.candidates[0].content.parts[0].text;

        // Clean JSON string in case standard markdown backticks are returned
        const cleanedJson = jsonString.replace(/```json/g, '').replace(/```/g, '').trim();
        const result = JSON.parse(cleanedJson);

        return NextResponse.json(result);

    } catch (error) {
        console.error("API Route Error:", error);
        return NextResponse.json({ error: "Failed to process assessment" }, { status: 500 });
    }
}
