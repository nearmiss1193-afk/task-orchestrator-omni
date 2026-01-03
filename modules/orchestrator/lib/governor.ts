import { GoogleGenerativeAI } from '@google/generative-ai';

export interface GovernorResult {
    approved: boolean;
    rewritten?: string;
    requiresManual?: boolean;
    reason?: string;
}

export class Governor {
    private genAI: GoogleGenerativeAI;
    private model: any;

    constructor() {
        const apiKey = process.env.GOOGLE_API_KEY || '';
        this.genAI = new GoogleGenerativeAI(apiKey);
        this.model = this.genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    }

    async check(draft: string, context: any = {}): Promise<GovernorResult> {
        console.log(`🛡️ [Governor] Checking draft: "${draft.substring(0, 50)}..."`);

        const prompt = `
        MISSION: Governor Protocol Activation.
        
        You are a safety filter for an automated "Ghost Responder" AI.
        
        DRAFT MESSAGE: "${draft}"
            MISSION: Governor Protocol Activation.
            Draft Message: "${draft}"
            Context: ${JSON.stringify(context)}
            
            Check:
            1. Is the tone too formal? (Should be Spartan: lowercase, no fluff)
            2. Is there any fake information about our pricing?
            
            Action: If the message feels like 'bot-speak', rewrite it in Spartan tone.
            
            Return JSON: { "approved": boolean, "rewritten": string | null, "reason": string }
            `;

        try {
            const result = await this.model.generateContent(prompt);
            const text = result.response.text().replace(/```json|```/g, '').trim();
            const decision = JSON.parse(text);

            if (decision.approved) {
                console.log('✅ [Governor] Draft Approved.');
            } else {
                console.warn(`⚠️ [Governor] Intervention: ${decision.reason}`);
            }

            return decision;

        } catch (error: any) {
            console.error('❌ [Governor] Check failed:', error.message);
            // Fail safe - require manual approval if governor breaks
            return { approved: false, requiresManual: true, reason: 'Governor Error' };
        }
    }
}
