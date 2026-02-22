import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
    try {
        const vapiKey = process.env.VAPI_PRIVATE_KEY;

        if (!vapiKey) {
            return NextResponse.json({ error: 'Missing VAPI_PRIVATE_KEY in Edge Environment.' }, { status: 500 });
        }

        // Specifically filter to the outbound Sovereign Assistant (ignoring Rachael inbound)
        const sovereignPhoneId = process.env.VAPI_PHONE_NUMBER_ID || '8a7f18bf-8c1e-4eaf-8fb9-53d308f54a0e';

        const response = await fetch(`https://api.vapi.ai/call?limit=50&phoneNumberId=${sovereignPhoneId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${vapiKey}`
            }
        });

        if (!response.ok) {
            console.error("Vapi Network Failure:", await response.text());
            throw new Error(`Vapi API responded with status: ${response.status}`);
        }

        const data = await response.json();
        return NextResponse.json(data);

    } catch (error: any) {
        console.error('Vapi Master Edge Error:', error);
        return NextResponse.json({ error: error.message || 'Internal API Bridge Timeout.' }, { status: 500 });
    }
}
