import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabaseClient';

export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
    try {
        const { template_name, action } = await req.json();

        if (!template_name || !action) {
            return NextResponse.json({ error: 'Missing template_name or action' }, { status: 400 });
        }

        // Map action to state value strings
        // e.g., 'pause' -> 'paused', 'live' -> 'live'
        const statusValue = action === 'pause' ? 'paused' : 'live';
        const stateKey = `campaign_${template_name}_status`;

        // Update or insert the per-template campaign state
        const { error } = await supabase
            .from('system_state')
            .upsert({
                key: stateKey,
                value: statusValue,
                description: `Operational status toggle for campaign template: ${template_name}`
            }, { onConflict: 'key' });

        if (error) throw error;

        return NextResponse.json({ success: true, template_name, status: statusValue });

    } catch (error: any) {
        console.error('Error in campaign-control route:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
