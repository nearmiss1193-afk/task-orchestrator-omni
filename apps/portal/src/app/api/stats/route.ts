import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL || '',
    process.env.SUPABASE_SERVICE_ROLE_KEY || ''
);

export async function GET() {
    try {
        // Get total leads count
        const { count: leadsCount } = await supabase
            .from('leads')
            .select('*', { count: 'exact', head: true });

        // Get pipeline value (sum of deals)
        const { data: deals } = await supabase
            .from('deals')
            .select('value')
            .eq('status', 'active');

        const pipelineValue = deals?.reduce((sum, d) => sum + (d.value || 0), 0) || 0;

        // Get call stats from today
        const today = new Date().toISOString().split('T')[0];
        const { count: callsToday } = await supabase
            .from('calls')
            .select('*', { count: 'exact', head: true })
            .gte('created_at', today);

        // Get reservations count
        const { count: reservations } = await supabase
            .from('reservations')
            .select('*', { count: 'exact', head: true });

        return NextResponse.json({
            success: true,
            data: {
                leads: leadsCount || 0,
                pipeline: pipelineValue,
                calls: callsToday || 0,
                reservations: reservations || 0,
                lastUpdated: new Date().toISOString()
            }
        });
    } catch (error) {
        // Fallback with mock data if Supabase not available
        return NextResponse.json({
            success: true,
            data: {
                leads: 127,
                pipeline: 48500,
                calls: 23,
                reservations: 8,
                lastUpdated: new Date().toISOString(),
                isMock: true
            }
        });
    }
}
