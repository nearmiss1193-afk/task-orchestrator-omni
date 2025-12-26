import { GHLConnector } from './connectors/ghl';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { PricingSpy } from './pricing-spy';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { createClient, SupabaseClient } from '@supabase/supabase-js';

// Simple mock for PDF generation if we don't have a heavy lib installed
// In a real scenario, use 'puppeteer' or 'html-pdf-node'
const generateMockPdf = async (content: string): Promise<string> => {
    // For now, checks if we can just send the markdown as the body or a link.
    // Nick's workflow mentions "Populate Markdown Proposal and convert to PDF".
    // We will simulate the PDF path for now.
    return "path/to/generated_proposal.pdf";
};

export class ProposalEngine {
    private ghl: GHLConnector;
    private genAI: GoogleGenerativeAI;
    private supabase: SupabaseClient;

    constructor() {
        this.ghl = new GHLConnector();
        this.genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY || '');
        this.supabase = createClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL || '',
            process.env.SUPABASE_SERVICE_ROLE_KEY || ''
        );
    }

    async processPostCall(contactId: string, conversationId?: string) {
        console.log(`📄 [ProposalEngine] Starting proposal generation for ${contactId}`);

        try {
            // 1. Fetch Transcript
            // If conversationId is missing, try to get the last conversation for this contact
            // This relies on GHL API features, simulating fetch here.
            const transcript = await this.getTranscript(contactId, conversationId);

            if (!transcript || transcript.length < 50) {
                console.warn('⚠️ [ProposalEngine] Transcript too short or missing. Aborting.');
                return;
            }

            // 2. Extract Data (Pain Points, Budget, Timeline)
            const extraction = await this.analyzeTranscript(transcript);

            // 2.5 Price Anchoring
            const pricingSpy = new PricingSpy();
            const anchorPrice = await pricingSpy.findCompetitorPricing("Service Business");

            // 2.8 VSL Scripting
            const vslScript = await this.generateVSLScript(extraction.pain_points, "Service Business"); // Context from transcript?

            // 3. Generate Proposal Content
            const proposalMarkdown = this.createProposalMarkdown(extraction, anchorPrice, vslScript);

            // 4. Convert to PDF (Simulated)
            // In reality, we might upload this HTML/MD to a service or use Puppeteer to print-to-pdf
            // For this implementation, we'll format it as an email body since direct PDF attachment via API can be tricky without upload steps.

            // 5. Send Email
            await this.ghl.execute('send_email', {
                contactId: contactId,
                subject: 'summary from our call - Nick', // As per spec
                body: `Here is the summary and proposal we discussed:\n\n${proposalMarkdown}`
                // attachments: [pdfPath] // If we had a real PDF url
            });

            console.log(`✅ [ProposalEngine] Proposal sent to ${contactId}`);

        } catch (error: any) {
            console.error('❌ [ProposalEngine] Failed:', error.message);
        }
    }

    private async getTranscript(contactId: string, conversationId?: string): Promise<string> {
        // Placeholder: Triggering GHL to get conversation.
        // Real implementation requires hitting GHL conversations endpoint.
        console.log(`Fetching transcript for ${contactId}...`);
        return ""; // TODO: Integration with real GHL Messages API
    }

    private async analyzeTranscript(transcript: string): Promise<any> {
        const model = this.genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
        const prompt = `
        MISSION: Extract critical sales info from this call transcript.
        TRANSCRIPT:
        """
        ${transcript.substring(0, 10000)}
        """
        
        EXTRACT:
        1. Pain Points: What specifically are they losing money on?
        2. Budget: Did they mention a price range? (If not, put "Unknown")
        3. Timeline: When do they want to start?
        
        Output JSON: { "pain_points": [], "budget": "...", "timeline": "..." }
        `;

        try {
            const result = await model.generateContent(prompt);
            const text = result.response.text().replace(/```json|```/g, '').trim();
            return JSON.parse(text);
        } catch (e) {
            console.error('AI Extraction failed');
            return { pain_points: ["Unknown"], budget: "Unknown", timeline: "Unknown" };
        }
    }

            return { pain_points: ["Unknown"], budget: "Unknown", timeline: "Unknown" };
        }
    }

    private async generateVSLScript(painPoints: string[], company: string): Promise < string > {
    const model = this.genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    const prompt = `
        MISSION: Write a 60-second VSL (Video Sales Letter) script.
        Target: ${company}
        Pain Points: ${painPoints.join(', ')}
        
        Framework: PAIN - AGITATION - SOLUTION.
        Tone: Spartan (Direct, Punchy, No Fluff).
        
        Output: Just the spoken words. No scene descriptions.
        `;

    try {
        const res = await model.generateContent(prompt);
        return res.response.text().trim();
    } catch(e) {
        return "Script generation failed.";
    }
}

    private createProposalMarkdown(data: any, anchorPrice: string, vslScript: string): string {
    return `
# Execution Plan

## Why we are doing this
${data.pain_points.map((p: string) => `- ${p}`).join('\n')}

## Market Analysis
**Standard Agency Pricing**: ${anchorPrice} (Competitor Average)
**Our Efficiency Model**: $1,500 setup + $500/mo

## Investment
**Budget Discussed**: ${data.budget}

## Timeline
**Target Start**: ${data.timeline}

## Next Steps
1. Sign agreement
2. Onboarding kick-off

## Personalized VSL Script (Read this to them)
> ${vslScript}
`;
}
}
