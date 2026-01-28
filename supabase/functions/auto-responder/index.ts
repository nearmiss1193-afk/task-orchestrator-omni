
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// Templates
const TEMPLATES: Record<string, any> = {
    "quote_request": {
        keywords: ["quote", "estimate", "price", "cost", "how much"],
        subject: "Re: Your Quote Request - AI Service Company",
        body: `Hi there!\n\nThank you for reaching out to AI Service Company!\n\nWe'd be happy to provide you with a free quote. To give you the most accurate estimate, could you please share:\n\n1. The type of service you need (HVAC, Plumbing, Roofing, etc.)\n2. Your location (City/Zip Code)\n3. A brief description of the issue or project\n\nAlternatively, you can call us directly at 1-(352) 758-5336 and speak with Sarah, our AI assistant, who can help you 24/7.\n\nLooking forward to helping you!\n\nBest regards,\nThe AI Service Company Team\nhttps://aiserviceco.com`
    },
    "appointment": {
        keywords: ["appointment", "schedule", "book", "available", "when can"],
        subject: "Re: Scheduling Your Appointment - AI Service Company",
        body: `Hi!\n\nThanks for wanting to schedule with us!\n\nYou can book an appointment instantly by:\n1. Calling 1-(352) 758-5336 (Sarah will help you find the perfect time)\n2. Visiting our website: https://aiserviceco.com\n\nWe have availability this week! What day works best for you?\n\nBest regards,\nThe AI Service Company Team`
    },
    "general_inquiry": {
        keywords: ["question", "help", "information", "inquiry"],
        subject: "Re: Your Inquiry - AI Service Company",
        body: `Hello!\n\nThank you for contacting AI Service Company!\n\nWe received your message and will get back to you within 24 hours. For immediate assistance, please call us at 1-(352) 758-5336.\n\nBest regards,\nThe AI Service Company Team`
    }
};

serve(async (req) => {
    if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

    try {
        const supabaseClient = createClient(
            Deno.env.get("SUPABASE_URL") ?? "",
            Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
        );

        const clientId = Deno.env.get("GMAIL_CLIENT_ID");
        const clientSecret = Deno.env.get("GMAIL_CLIENT_SECRET");
        const refreshToken = Deno.env.get("GMAIL_REFRESH_TOKEN");

        if (!clientId || !clientSecret || !refreshToken) throw new Error("Missing Gmail Credentials");

        // 1. Refresh Token
        const tokenResp = await fetch("https://oauth2.googleapis.com/token", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
                client_id: clientId,
                client_secret: clientSecret,
                refresh_token: refreshToken,
                grant_type: "refresh_token",
            }),
        });
        const accessToken = (await tokenResp.json()).access_token;
        if (!accessToken) throw new Error("Failed to refresh token");

        // 2. List Unread Emails
        const listResp = await fetch(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages?q=is:unread&maxResults=10",
            { headers: { Authorization: `Bearer ${accessToken}` } }
        );
        const messages = (await listResp.json()).messages || [];
        console.log(`Found ${messages.length} unread emails`);

        let sent = 0;

        for (const msg of messages) {
            const msgResp = await fetch(
                `https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}`,
                { headers: { Authorization: `Bearer ${accessToken}` } }
            );
            const email = await msgResp.json();

            const headers = email.payload?.headers || [];
            const from = headers.find((h: any) => h.name === "From")?.value || "";
            const subject = headers.find((h: any) => h.name === "Subject")?.value || "";
            const snippet = email.snippet || "";

            // Skip invalid
            if (from.includes("no-reply") || from.includes("aiserviceco.com")) continue;

            // Determine Intent
            const content = (subject + " " + snippet).toLowerCase();
            let intent = "general_inquiry";

            for (const [key, tpl] of Object.entries(TEMPLATES)) {
                if (tpl.keywords.some((k: string) => content.includes(k))) {
                    intent = key;
                    break;
                }
            }

            console.log(`📧 Responding to ${from} with ${intent}`);

            // Send Reply
            // Note: Gmail API requires base64url encoded raw message. 
            // Simplified for this mock - production needs full MIME construction

            const template = TEMPLATES[intent];
            const rawMessage = [
                `To: ${from}`,
                `Subject: ${template.subject}`,
                `Content-Type: text/plain; charset="UTF-8"`,
                ``,
                template.body
            ].join("\n");

            // Base64URL Encode
            const encodedMessage = btoa(rawMessage).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

            await fetch(
                `https://gmail.googleapis.com/gmail/v1/users/me/messages/send`,
                {
                    method: "POST",
                    headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
                    body: JSON.stringify({ raw: encodedMessage }),
                }
            );

            // Mark Read
            await fetch(
                `https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}/modify`,
                {
                    method: "POST",
                    headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
                    body: JSON.stringify({ removeLabelIds: ["UNREAD"] }),
                }
            );

            sent++;

            // Log
            await supabaseClient.from("system_logs").insert({
                level: "INFO",
                message: `Auto-Response Sent: ${intent}`,
                metadata: { to: from, intent },
                created_at: new Date().toISOString(),
            });
        }

        return new Response(
            JSON.stringify({ status: "success", sent }),
            { headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );

    } catch (error) {
        console.error(error);
        return new Response(JSON.stringify({ error: error.message }), { status: 500, headers: corsHeaders });
    }
});
