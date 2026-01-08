import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"
import Stripe from "https://esm.sh/stripe@12.0.0"

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY') ?? '', {
    apiVersion: '2022-11-15',
    httpClient: Stripe.createFetchHttpClient(),
})

const cryptoProvider = Stripe.createSubtleCryptoProvider()

serve(async (req) => {
    const signature = req.headers.get('Stripe-Signature')
    const body = await req.text()

    let event
    try {
        event = await stripe.webhooks.constructEventAsync(
            body,
            signature,
            Deno.env.get('STRIPE_WEBHOOK_SECRET') ?? '',
            undefined,
            cryptoProvider
        )
    } catch (err) {
        return new Response(err.message, { status: 400 })
    }

    // Initialize Supabase Admin Client
    const supabase = createClient(
        Deno.env.get('SUPABASE_URL') ?? '',
        Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Handle Event
    if (event.type === 'checkout.session.completed') {
        const session = event.data.object
        const customerEmail = session.customer_details?.email

        // Provision User: Insert into organizations/subscriptions tables
        // For now, we push to tasks_queue for the Python Worker to handle complex provisioning (e.g. creating DBs)

        const { error } = await supabase.from('tasks_queue').insert({
            task_type: 'provision_account',
            payload: {
                stripe_session_id: session.id,
                email: customerEmail,
                customer_id: session.customer
            },
            status: 'pending'
        })

        if (error) console.error('Error inserting task:', error)
    }

    return new Response(JSON.stringify({ received: true }), {
        headers: { 'Content-Type': 'application/json' },
    })
})
