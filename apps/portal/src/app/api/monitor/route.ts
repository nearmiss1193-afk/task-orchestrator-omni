import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabaseClient';

export const dynamic = 'force-dynamic';

export async function GET() {
    try {
        // 1. Regional Offensive (AEO / SEO Audit)
        const { count: outbound24h, error: err1 } = await supabase
            .from('outbound_touches')
            .select('*', { count: 'exact', head: true })
            .gte('ts', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString());

        // 2. Bid-Bot (B2G)
        const { count: bids24h, error: err2 } = await supabase
            .from('bids')
            .select('*', { count: 'exact', head: true })
            .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString());

        // 3. Intent Engine (B2C)
        const { count: estates24h, error: err3 } = await supabase
            .from('estate_sales')
            .select('*', { count: 'exact', head: true })
            .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString());

        // 4. Social / System State
        const { data: systemData, error: err4 } = await supabase
            .from('system_state')
            .select('key, status');

        // Extract specific health/state keys
        let campaignMode = 'active';
        let latestHeartbeat = 'Just Now';
        if (systemData) {
            const cm = systemData.find(s => s.key === 'campaign_mode');
            if (cm) campaignMode = cm.status;
        }

        const { data: healthData } = await supabase
            .from('system_health_log')
            .select('checked_at')
            .order('checked_at', { ascending: false })
            .limit(1);

        if (healthData && healthData.length > 0) {
            latestHeartbeat = new Date(healthData[0].checked_at).toLocaleTimeString();
        }

        const payload = {
            regional_outbound_24h: outbound24h || 0,
            bid_bot_24h: bids24h || 0,
            intent_engine_24h: estates24h || 0,
            campaign_mode: campaignMode,
            last_heartbeat: latestHeartbeat,
            seo_factory_status: 'Active (Hourly)'
        };

        return NextResponse.json(payload, { status: 200 });

    } catch (err: any) {
        console.error('API /monitor Error:', err);
        return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
    }
}
