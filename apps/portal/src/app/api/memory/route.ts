import { NextResponse } from 'next/server';
import { createClient, SupabaseClient } from '@supabase/supabase-js';

function getSupabase(): SupabaseClient | null {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    if (!url || !key) return null;
    return createClient(url, key);
}

// GET - Retrieve memories for a caller
export async function GET(request: Request) {
    const supabase = getSupabase();
    const { searchParams } = new URL(request.url);
    const phone = searchParams.get('phone');
    const agentId = searchParams.get('agent_id') || 'listen-linda';

    if (!phone) {
        return NextResponse.json({ error: 'phone parameter required' }, { status: 400 });
    }

    if (!supabase) {
        return NextResponse.json({ success: true, memories: [], isMock: true });
    }

    try {
        const { data, error } = await supabase
            .from('agent_memory')
            .select('*')
            .eq('user_phone', phone)
            .eq('agent_id', agentId)
            .order('created_at', { ascending: false })
            .limit(10);

        if (error) throw error;

        return NextResponse.json({ success: true, memories: data });
    } catch (error) {
        return NextResponse.json({ success: false, memories: [] });
    }
}

// POST - Store new memory
export async function POST(request: Request) {
    const supabase = getSupabase();

    if (!supabase) {
        return NextResponse.json({ success: false, error: 'Database not configured' }, { status: 500 });
    }

    try {
        const body = await request.json();
        const { phone, agent_id = 'listen-linda', context, memory_type = 'conversation' } = body;

        if (!phone || !context) {
            return NextResponse.json({ error: 'phone and context required' }, { status: 400 });
        }

        const { data, error } = await supabase
            .from('agent_memory')
            .insert([{ user_phone: phone, agent_id, context, memory_type }])
            .select()
            .single();

        if (error) throw error;

        return NextResponse.json({ success: true, memory: data });
    } catch (error) {
        return NextResponse.json({ success: false, error: 'Failed to store memory' }, { status: 500 });
    }
}

// DELETE - Clear memory by ID
export async function DELETE(request: Request) {
    const supabase = getSupabase();
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) {
        return NextResponse.json({ error: 'id parameter required' }, { status: 400 });
    }

    if (!supabase) {
        return NextResponse.json({ success: false, error: 'Database not configured' }, { status: 500 });
    }

    try {
        const { error } = await supabase
            .from('agent_memory')
            .delete()
            .eq('id', id);

        if (error) throw error;

        return NextResponse.json({ success: true });
    } catch (error) {
        return NextResponse.json({ success: false, error: 'Failed to delete memory' }, { status: 500 });
    }
}
