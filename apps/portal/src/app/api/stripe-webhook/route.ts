import { NextResponse } from 'next/server';
import Stripe from 'stripe';
import fetch from 'node-fetch';
import { Resend } from 'resend';

// CORS headers
const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Stripe-Signature',
};

export async function OPTIONS() {
    return NextResponse.json({}, { headers: corsHeaders });
}

export async function POST(req: Request) {
    const sig = req.headers.get('stripe-signature') || '';
    const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
    const stripeKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeKey || !webhookSecret) {
        console.error('[WEBHOOK] Missing Stripe config');
        return NextResponse.json({ error: 'Misconfiguration' }, { status: 500, headers: corsHeaders });
    }
    const stripe = new Stripe(stripeKey, { apiVersion: '2025-12-15.clover' });
    let event;
    try {
        const rawBody = await req.text();
        event = stripe.webhooks.constructEvent(rawBody, sig, webhookSecret);
    } catch (err) {
        console.error('[WEBHOOK] Signature verification failed', err);
        return NextResponse.json({ error: 'Invalid signature' }, { status: 400, headers: corsHeaders });
    }
    // Handle checkout.session.completed
    if (event.type === 'checkout.session.completed') {
        const session = event.data.object as any;
        const customerEmail = session.customer_details?.email;
        const customerName = session.metadata?.customer_name || '';
        const customerPhone = session.metadata?.customer_phone || '';
        const plan = session.metadata?.plan || '';
        // 1. Add contact to GHL
        const ghlToken = process.env.GHL_AGENCY_API_TOKEN;
        const ghlLocation = process.env.GHL_LOCATION_ID;
        if (ghlToken && ghlLocation) {
            const ghlUrl = `https://rest.gohighlevel.com/v1/contacts`;
            const contactBody = {
                locationId: ghlLocation,
                firstName: customerName,
                email: customerEmail,
                phone: customerPhone,
                customFields: [{ name: 'Plan', value: plan }],
                tags: ['client-onboarded']
            };
            try {
                await fetch(ghlUrl, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${ghlToken}`, 'Content-Type': 'application/json' },
                    body: JSON.stringify(contactBody)
                });
            } catch (e) {
                console.error('[GHL] Failed to create contact', e);
            }
        }
        // 2. Send welcome email via Resend
        const resendKey = process.env.RESEND_API_KEY;
        if (resendKey && customerEmail) {
            const resend = new Resend(resendKey);
            try {
                await resend.emails.send({
                    from: 'welcome@aiserviceco.com',
                    to: customerEmail,
                    subject: 'Welcome to AI Service Co – HomeHeart HVAC',
                    html: `<p>Hi ${customerName},</p><p>Thank you for joining our AI‑powered HVAC automation platform. Your trial starts now – feel free to explore the dashboard.</p><p>Best,<br/>The AI Service Co Team</p>`
                });
            } catch (e) {
                console.error('[RESEND] Email send failed', e);
            }
        }
    }
    return NextResponse.json({ received: true }, { headers: corsHeaders });
}
