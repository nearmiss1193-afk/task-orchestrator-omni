import { NextResponse } from 'next/server';
import { supabase } from '@/lib/supabaseClient';

export const dynamic = 'force-dynamic';

export async function GET() {
    try {
        // We will calculate a 7-day trailing velocity
        const now = new Date();
        const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

        // 1. Get Pipeline Funnel Size
        const { count: pipelineSize, error: pipeErr } = await supabase
            .from('contacts_master')
            .select('*', { count: 'exact', head: true })
            .in('status', ['new', 'research_done']);

        if (pipeErr) throw pipeErr;

        // 2. Get Open / Reply Telemetry Velocity
        const { data: recentTouches, error: touchErr } = await supabase
            .from('outbound_touches')
            .select('status, opened, ts')
            .gte('ts', thirtyDaysAgo.toISOString())
            .or('status.eq.replied,opened.eq.true');

        if (touchErr) throw touchErr;

        let opens7d = 0;
        let replies7d = 0;
        let replies30d = 0;

        recentTouches.forEach((t: any) => {
            const touchDate = new Date(t.ts);
            const isWithin7d = touchDate >= sevenDaysAgo;

            if (t.opened === true || t.status === 'opened') {
                if (isWithin7d) opens7d++;
            }
            if (t.status === 'replied') {
                replies30d++;
                if (isWithin7d) replies7d++;
            }
        });

        // 3. Predictive Math Model
        // Calculate the trailing 30 day reply conversion rate (proxy using average daily replies)
        const dailyReplyRate = replies30d / 30;

        // Predict weekly bookings based on reply velocity and pipeline
        // Assumption: 1 in 4 replies lead to a booking, and pipeline sustains the velocity
        const predictedWeeklyReplies = dailyReplyRate * 7;
        const predictedWeeklyBookings = Math.round(predictedWeeklyReplies * 0.25);

        // Calculate a 'Pipeline Health' score based on opens and replies relative to an ideal threshold
        const healthScore = Math.min(100, Math.round((replies7d * 5 + opens7d) / 5));

        return NextResponse.json({
            pipeline_size: pipelineSize || 0,
            velocity_7d: {
                opens: opens7d,
                replies: replies7d
            },
            forecast: {
                predicted_weekly_bookings: predictedWeeklyBookings,
                pipeline_health_score: healthScore,
                sustainability: pipelineSize && pipelineSize > 1000 ? 'High' : 'Low'
            }
        });

    } catch (error: any) {
        console.error('Error in revenue forecast:', error);
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
