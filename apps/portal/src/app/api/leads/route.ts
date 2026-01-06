import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '20');
    const offset = parseInt(searchParams.get('offset') || '0');

    try {
        const { data: leads, error } = await supabase
            .from('leads')
            .select('*')
            .order('created_at', { ascending: false })
            .range(offset, offset + limit - 1);

        if (error) throw error;

        return NextResponse.json({
            success: true,
            data: leads,
            pagination: {
                limit,
                offset,
                hasMore: (leads?.length || 0) === limit
            }
        });
    } catch (error) {
        // Return mock data if Supabase not available
        return NextResponse.json({
            success: true,
            data: [
                { id: 1, name: 'John Smith', email: 'john@hvacpro.com', phone: '555-0101', status: 'captured', source: 'HVAC Landing', created_at: new Date().toISOString() },
                { id: 2, name: 'Maria Garcia', email: 'maria@coolingsolutions.com', phone: '555-0102', status: 'call_scheduled', source: 'Direct', created_at: new Date().toISOString() },
                { id: 3, name: 'HomeHeart HVAC', email: 'info@homehearthvac.com', phone: '555-0103', status: 'hot', source: 'Campaign', created_at: new Date().toISOString() }
            ],
            pagination: { limit, offset, hasMore: false },
            isMock: true
        });
    }
}

export async function POST(request: Request) {
    try {
        const body = await request.json();
        const { name, email, phone, source, notes } = body;

        const { data, error } = await supabase
            .from('leads')
            .insert([{ name, email, phone, source, notes, status: 'new' }])
            .select()
            .single();

        if (error) throw error;

        return NextResponse.json({ success: true, data });
    } catch (error) {
        return NextResponse.json({ success: false, error: 'Failed to create lead' }, { status: 500 });
    }
}
