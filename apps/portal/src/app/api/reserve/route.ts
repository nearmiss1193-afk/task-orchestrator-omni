import { NextResponse } from 'next/server';

// CORS headers for cross-origin requests from checkout forms
const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
};

export async function OPTIONS() {
    return NextResponse.json({}, { headers: corsHeaders });
}

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const { name, email, phone, plan } = body;

        console.log('[RESERVE] New reservation:', { name, email, phone, plan });

        // TODO: Connect to Supabase or GHL to save lead
        // For now, we'll simulate success

        // In production, add to GHL CRM:
        // const ghlRes = await addToGHL({ name, email, phone, plan });

        return NextResponse.json({
            status: 'success',
            message: 'Reservation saved',
            data: { name, email, phone, plan }
        }, { headers: corsHeaders });

    } catch (error) {
        console.error('[RESERVE] Error:', error);
        return NextResponse.json({
            status: 'error',
            message: 'Failed to save reservation'
        }, { status: 500, headers: corsHeaders });
    }
}
