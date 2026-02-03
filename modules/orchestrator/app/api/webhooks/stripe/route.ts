import { NextResponse } from 'next/server';
import { NotionConnector } from '@/lib/connectors/notion';
import axios from 'axios';

// Initialize Notion
const notion = new NotionConnector();

export async function POST(req: Request) {
    const body = await req.text();
    const sig = req.headers.get('stripe-signature');

    // In a real app, verify signature with Stripe SDK
    // import Stripe from 'stripe'; const stripe = ...; stripe.webhooks.constructEvent(...)

    console.log("💰 [StripeWebhook] Payment event received.");

    try {
        const event = JSON.parse(body);

        if (event.type === 'checkout.session.completed') {
            const session = event.data.object;

            const clientName = session.customer_details?.name || "Unknown Client";
            const clientEmail = session.customer_details?.email || "No Email";
            const amount = session.amount_total ? session.amount_total / 100 : 0;
            const plan = (amount > 2000) ? "Growth Partner ($3k)" : "Starter ($1.5k)";

            console.log(`🎉 New Sale: ${clientName} (${plan})`);

            // 1. Create Notion Dashboard
            const dashboardUrl = await notion.createClientDashboard(clientName, plan);

            // 2. Send Slack Alert
            await sendSlackAlert(clientName, plan, amount, dashboardUrl);

            // 3. (Optional) Trigger GHL via Webhook or API to tag 'paid_client'
            // await triggerGHL(clientEmail, "paid_client");

            return NextResponse.json({ received: true });
        }

        return NextResponse.json({ received: true, status: "ignored_type" });

    } catch (err: any) {
        console.error(`❌ Webhook Error: ${err.message}`);
        return NextResponse.json({ error: "Webhook Failed" }, { status: 400 });
    }
}

async function sendSlackAlert(name: string, plan: string, amount: number, url: string) {
    const slackUrl = process.env.SLACK_WEBHOOK_URL;
    if (!slackUrl) {
        console.log("⚠️ No SLACK_WEBHOOK_URL. Logging alert:", `New Sale: ${name}, ${plan}, ${url}`);
        return;
    }

    await axios.post(slackUrl, {
        text: `💰 *NEW CLIENT SECURED* 💰\n\n*Client:* ${name}\n*Plan:* ${plan} ($${amount})\n*Dashboard:* ${url}\n\n_Spartan Protocol Initiated._`
    });
}
