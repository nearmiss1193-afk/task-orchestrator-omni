import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
    const envDump = {
        supabaseUrl: process.env.NEXT_PUBLIC_SUPABASE_URL || 'MISSING',
        supabaseAnonKeyPrefix: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ? process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY.substring(0, 10) : 'MISSING',
        vapiKeyPrefix: process.env.VAPI_PRIVATE_KEY ? process.env.VAPI_PRIVATE_KEY.substring(0, 10) : 'MISSING',
    };

    return NextResponse.json(envDump);
}
