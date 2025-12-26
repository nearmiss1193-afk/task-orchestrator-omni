
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { GHLConnector } from './connectors/ghl';
import { GoogleGenerativeAI } from '@google/generative-ai';

export class GhostResponder {
    private supabase: SupabaseClient;
    private ghl: GHLConnector;
    private genAI: GoogleGenerativeAI;

    constructor() {
        this.supabase = createClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL || '',
            process.env.SUPABASE_SERVICE_ROLE_KEY || ''
        );
        this.ghl = new GHLConnector();
        this.genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY || '');
    }

    async handleInbound(payload: any) {
        const contactId = payload.contactId;
        const messageBody = payload.body;
        console.log(`👻 [GhostResponder] Processing inbound from ${contactId}: "${messageBody}"`);

        try {
            // 1. Get Context from Supabase
            const { data: contact } = await this.supabase
                .from('contacts_master')
                .select('*')
                .eq('ghl_contact_id', contactId)
                .single();

            // 2. Draft Reply with AI
            const model = this.genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
            const prompt = `
                You are a helpful AI assistant for AI Service Co. 
                Lead Context: ${JSON.stringify(contact || {})}
                Inbound Message: "${messageBody}"
                Role: Be concise, friendly, and helpful. Goal is to book an appointment or answer questions about Missed Call AI/Vortex Audits.
                Output format: JSON { "reply": "...", "confidence": 0-1 }
            `;

            const result = await model.generateContent(prompt);
            const responseText = result.response.text();
            const cleaned = responseText.replace(/```json|```/g, '').trim();
            const { reply, confidence } = JSON.parse(cleaned);

            // 3. Turbo Mode: Auto-Send if Confidence is high
            const autoSendThreshold = 0.8;
            let status = 'staged';

            if (confidence >= autoSendThreshold) {
                console.log(`🚀 [Turbo] Auto-sending high-confidence reply (${confidence})`);
                await this.ghl.execute('send_sms', {
                    contactId,
                    body: reply
                });
                status = 'sent';
            }

            // 4. Record in staged_replies
            await this.supabase.from('staged_replies').insert({
                contact_id: contactId,
                draft_content: reply,
                status: status,
                confidence: confidence,
                platform: payload.type || 'sms'
            });

            return { success: true, status, reply };

        } catch (error: any) {
            console.error("❌ [GhostResponder] Failed:", error.message);
            return { success: false, error: error.message };
        }
    }
}
