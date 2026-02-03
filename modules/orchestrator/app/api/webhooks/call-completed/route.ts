import { NextRequest, NextResponse } from 'next/server';
import { ProposalEngine } from '@/lib/proposal-engine';

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        console.log('📞 [Webhook] Call Completed payload received:', JSON.stringify(body, null, 2));

        // Basic validation - check for contactId at minimum
        if (!body.contact_id && !body.contactId) {
            return NextResponse.json({ error: 'Missing contact_id' }, { status: 400 });
        }

        const contactId = body.contact_id || body.contactId;
        const conversationId = body.conversation_id || body.conversationId;

        // Trigger Proposal Engine
        const engine = new ProposalEngine();

        // We run this asynchronously so we don't block the webhook response
        engine.processPostCall(contactId, conversationId).catch(err => {
            console.error('❌ [ProposalEngine] Async processing failed:', err);
        });

        return NextResponse.json({ success: true, message: 'Processing started' });
    } catch (error: any) {
        console.error('❌ [Webhook] Error processing call completed:', error);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
