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

    /**
     * Extracts deep-dive links from a Playwright page.
     */
    async scanForDeepLinks(page: any, baseUrl: string): Promise<string[]> {
        try {
            const links = await page.$$eval('a', (anchors: any[]) => anchors.map((a: any) => a.href));
            const uniqueLinks = Array.from(new Set(links)) as string[];

            return uniqueLinks.filter(href => {
                const lower = href.toLowerCase();
                return ['about', 'team', 'career', 'jobs', 'press', 'news'].some(kw => lower.includes(kw)) &&
                    href.includes(baseUrl); // Keep it internal
            }).slice(0, 3);
        } catch (e) {
            console.warn("Deep link scan failed", e);
            return [];
        }
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
    /**
     * Calculates the OMNI-TURBO Vibe Score based on research features.
     * Criteria:
     * - No Lead Magnet: -20
     * - No Recent Reviews: -30
     * - Slow Mobile Load: -10
     */
    calculateVibeScore(features: { hasLeadMagnet: boolean, hasRecentReviews: boolean, mobileLoadSpeed: 'fast' | 'slow' }): number {
        let score = 100;

        if (!features.hasLeadMagnet) {
            score -= 20;
        }
        if (!features.hasRecentReviews) {
            score -= 30;
        }
        if (features.mobileLoadSpeed === 'slow') {
            score -= 25; // Spartan Penalty (Agitator Logic)
        }

        return Math.max(0, score); // Ensure score doesn't go below 0
    }
}
