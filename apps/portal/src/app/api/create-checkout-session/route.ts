import { NextResponse } from 'next/server';
import Stripe from 'stripe';

// CORS headers for cross-origin requests
const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
};

// Plan pricing configuration
const PLANS: Record<string, { name: string; price: number; priceId?: string }> = {
    starter: { name: 'HVAC Starter', price: 9900 }, // $99 in cents
    lite: { name: 'HVAC Lite', price: 19900 },      // $199 in cents
    growth: { name: 'HVAC Growth', price: 29700 },  // $297 in cents
};

export async function OPTIONS() {
    return NextResponse.json({}, { headers: corsHeaders });
}

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const { name, email, phone, plan = 'starter' } = body;

        const stripeKey = process.env.STRIPE_SECRET_KEY;

        if (!stripeKey) {
            console.error('[STRIPE] No STRIPE_SECRET_KEY configured');
            return NextResponse.json({
                status: 'error',
                message: 'Stripe not configured. Please contact support at (863) 213-2505.'
            }, { status: 500, headers: corsHeaders });
        }

        const stripe = new Stripe(stripeKey, { apiVersion: '2024-06-20' });
        const selectedPlan = PLANS[plan] || PLANS.starter;

        console.log('[STRIPE] Creating checkout session for:', { name, email, plan: selectedPlan.name });

        // Create Stripe Checkout Session with 14-day trial
        const session = await stripe.checkout.sessions.create({
            payment_method_types: ['card'],
            mode: 'subscription',
            customer_email: email,
            line_items: [
                {
                    price_data: {
                        currency: 'usd',
                        product_data: {
                            name: selectedPlan.name,
                            description: `AI Automation for HVAC businesses - 14-Day Money-Back Guarantee`,
                        },
                        unit_amount: selectedPlan.price,
                        recurring: {
                            interval: 'month',
                        },
                    },
                    quantity: 1,
                },
            ],
            subscription_data: {
                trial_period_days: 14, // 14-day trial as standardized
                metadata: {
                    customer_name: name,
                    customer_phone: phone,
                    plan: plan,
                },
            },
            success_url: `${process.env.NEXT_PUBLIC_BASE_URL || 'https://www.aiserviceco.com'}/success?session_id={CHECKOUT_SESSION_ID}`,
            cancel_url: `${process.env.NEXT_PUBLIC_BASE_URL || 'https://www.aiserviceco.com'}/checkout?plan=${plan}&cancelled=true`,
            metadata: {
                customer_name: name,
                customer_phone: phone,
            },
        });

        console.log('[STRIPE] Session created:', session.id);

        return NextResponse.json({
            status: 'success',
            url: session.url,
            sessionId: session.id
        }, { headers: corsHeaders });

    } catch (error: any) {
        console.error('[STRIPE] Error:', error.message);
        return NextResponse.json({
            status: 'error',
            message: error.message || 'Failed to create checkout session'
        }, { status: 500, headers: corsHeaders });
    }
}
