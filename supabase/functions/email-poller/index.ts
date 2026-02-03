
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
    if (req.method === "OPTIONS") {
        return new Response("ok", { headers: corsHeaders });
    }

    try {
        const supabaseClient = createClient(
            Deno.env.get("SUPABASE_URL") ?? "",
            Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""
        );

        // Get Gmail Credentials from Vault (Stored in DB or Env)
        // NOTE: For Edge Functions, we typically store these in Vault Table or Env
        const clientId = Deno.env.get("GMAIL_CLIENT_ID");
        const clientSecret = Deno.env.get("GMAIL_CLIENT_SECRET");
        const refreshToken = Deno.env.get("GMAIL_REFRESH_TOKEN");

        if (!clientId || !clientSecret || !refreshToken) {
            throw new Error("Missing Gmail Credentials");
        }

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

        const tokenData = await tokenResp.json();
        const accessToken = tokenData.access_token;

        if (!accessToken) throw new Error("Failed to refresh Gmail token");

        // 2. List Unread Emails
        const listResp = await fetch(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages?q=is:unread&maxResults=20",
            { headers: { Authorization: `Bearer ${accessToken}` } }
        );
        const listData = await listResp.json();
        const messages = listData.messages || [];

        console.log(`Found ${messages.length} unread emails`);

        let leadsFound = 0;

        // 3. Process Emails
        for (const msg of messages) {
            const msgResp = await fetch(
                `https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}`,
                { headers: { Authorization: `Bearer ${accessToken}` } }
            );
            const email = await msgResp.json();

            const payload = email.payload || {};
            const headers = payload.headers || [];
            const subjectHeader = headers.find((h: any) => h.name === "Subject");
            const fromHeader = headers.find((h: any) => h.name === "From");
            const subject = subjectHeader ? subjectHeader.value : "";
            const from = fromHeader ? fromHeader.value : "";
            const snippet = email.snippet || "";

            // Lead Detection Logic
            const leadKeywords = ["quote", "estimate", "service", "hvac", "plumbing", "book", "interested"];
            const content = (subject + " " + snippet).toLowerCase();
            const isLead = leadKeywords.some((k) => content.includes(k));

            if (isLead) {
                console.log(`🎯 LEAD: ${from} - ${subject}`);
                leadsFound++;

                // Log to Supabase
                await supabaseClient.from("system_logs").insert({
                    level: "LEAD",
                    message: `New Lead Detected: ${from}`,
                    metadata: { from, subject, snippet },
                    created_at: new Date().toISOString(),
                });

                // Mark as Read
                await fetch(
                    `https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}/modify`,
                    {
                        method: "POST",
                        headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
                        body: JSON.stringify({ removeLabelIds: ["UNREAD"] }),
                    }
                );
            }
        }

        return new Response(
            JSON.stringify({ status: "success", leads_found: leadsFound }),
            { headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );

    } catch (error) {
        console.error(error);
        return new Response(
            JSON.stringify({ error: error.message }),
            { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
    }
});
