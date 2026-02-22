import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import twilio from 'twilio';
import { Resend } from 'resend';

// Vercel serverless requires dynamic execution for database/telephony integrations
export const dynamic = 'force-dynamic';

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const { contact_identifier, channel, body: messageText } = body;

        if (!contact_identifier || !messageText) {
            return NextResponse.json({ error: 'Missing target identifier or payload body' }, { status: 400 });
        }

        // Initialize Service Role Supabase Client (bypassing RLS for backend execution)
        const supabase = createClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL || '',
            process.env.SUPABASE_SERVICE_ROLE_KEY || ''
        );

        // 1. Fetch Contact to retrieve explicit Phone/Email bindings
        const { data: leads, error: leadError } = await supabase
            .from('contacts_master')
            .select('id, phone, email')
            .or(`phone.eq.${contact_identifier},email.eq.${contact_identifier}`)
            .limit(1);

        if (leadError || !leads || leads.length === 0) {
            return NextResponse.json({ error: 'Contact vector not found in database' }, { status: 404 });
        }

        const lead = leads[0];

        // 2. Lock the AI logic (ai_paused: true)
        const { error: lockError } = await supabase
            .from('contacts_master')
            .update({ ai_paused: true })
            .eq('id', lead.id);

        if (lockError) console.error("Warning: Failed to establish AI lock:", lockError);

        // 3. Dispatch the manual payload via Telephony/Email REST APIs
        let sendStatus = 'delivered';

        if (channel === 'sms' && lead.phone) {
            try {
                const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);
                await client.messages.create({
                    body: messageText,
                    from: process.env.TWILIO_FROM_NUMBER,
                    to: lead.phone
                });
            } catch (smsError) {
                console.error("Twilio Dispatch Failed:", smsError);
                sendStatus = 'failed';
            }
        } else if (channel === 'email' && lead.email) {
            try {
                const resend = new Resend(process.env.RESEND_API_KEY);
                // Use the validated owner namespace for verified routing
                await resend.emails.send({
                    from: 'Sovereign Empire <owner@aiserviceco.com>',
                    to: [lead.email],
                    subject: 'Priority Update',
                    text: messageText
                });
            } catch (emailError) {
                console.error("Resend Dispatch Failed:", emailError);
                sendStatus = 'failed';
            }
        } else {
            sendStatus = 'failed_no_channel';
        }

        // 4. Inject Verified Omniscient Log into the Telemetry Tracker
        const { data: touchData, error: touchError } = await supabase
            .from('outbound_touches')
            .insert({
                lead_id: lead.id,
                phone: lead.phone,
                email: lead.email,
                channel: channel,
                direction: 'outbound',
                status: sendStatus,
                body: messageText,
                ts: new Date().toISOString()
            })
            .select();

        if (touchError) {
            console.error("Database Telemetry Logging Failed:", touchError);
            return NextResponse.json({ error: 'Message sent but database logging failed' }, { status: 500 });
        }

        // Return the authorized database row so the React UI can update optimistically
        return NextResponse.json({
            success: true,
            status: sendStatus,
            data: touchData[0]
        });

    } catch (err: any) {
        console.error('Manual Override Terminal Failure:', err);
        return NextResponse.json({ error: 'Internal Server Error', details: err.message }, { status: 500 });
    }
}
