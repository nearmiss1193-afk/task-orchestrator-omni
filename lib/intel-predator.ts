import { GoogleGenerativeAI } from '@google/generative-ai';

export class IntelPredator {
    private genAI: GoogleGenerativeAI;
    private model: any;

    constructor() {
        const apiKey = process.env.GOOGLE_API_KEY || '';
        this.genAI = new GoogleGenerativeAI(apiKey);
        // Using gemini-1.5-flash for consistent, fast intelligence synthesis
        this.model = this.genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    }

    async generateDossier(personInfo: any, researchData: any): Promise<string> {
        const prompt = `
        MISSION: INTEL PREDATOR DEEP-DIVE
        ROLE: Elite Intelligence Analyst (Mossad/CIA style precision).
        
        SUBJECT: ${personInfo.name}
        COMPANY: ${personInfo.company}
        
        RESEARCH DATA:
        ${JSON.stringify(researchData, null, 2)}
        
        TASK:
        Generate a comprehensive, high-stakes "Battle Card" dossier. 
        I need to know exactly WHO this person is so I can close them.
        
        CATEGORIES REQUIRED:
        - **Core Interests & Passions**: (Stated vs Inferred)
        - **Hobbies & Lifestyle**: (Likes, Dislikes, Weekend activities)
        - **Family & Personal**: (If available - keep it professional but deep)
        - **Worldview & Values**: (Religious/Political leanings if detectable)
        - **Decision-Maker Persona**: (Aggressive, Analytical, Visionary, etc.)
        - **Proposed Conversation Starter**: (A 1-sentence hook that feels like we've known them for years)
        
        STYLE:
        - Spartan, objective, and precise.
        - Bullet points ONLY.
        - Every single point must be labeled [STATED] or [INFERRED].
        `;

        try {
            const result = await this.model.generateContent(prompt);
            const response = await result.response;
            return response.text().trim();
        } catch (error: any) {
            console.error('Dossier Synthesis failed:', error.message);
            return 'Dossier Synthesis failed.';
        }
    }
}
