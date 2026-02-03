
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// Configuration
const HEALTH_CHECKS = {
    "website": "https://aiserviceco.com",
    // Add other critical endpoints here
};

const CRITICAL_TABLES = ["prospects", "email_logs", "system_logs"];
const ALERT_EMAIL = "owner@aiserviceco.com";

serve(async (req) => {
    if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });

    try {
        const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
        const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
        const resendApiKey = Deno.env.get("RESEND_API_KEY");

        const supabase = createClient(supabaseUrl, supabaseKey);
        const issues: string[] = [];

        // 1. Check Endpoints
        for (const [name, url] of Object.entries(HEALTH_CHECKS)) {
            try {
                const res = await fetch(url);
                if (!res.ok) issues.push(`Endpoint ${name} returned ${res.status}`);
            } catch (e) {
                issues.push(`Endpoint ${name} failed: ${e.message}`);
            }
        }

        // 2. Check Database Tables
        for (const table of CRITICAL_TABLES) {
            const { error } = await supabase.from(table).select("*").limit(1);
            if (error) issues.push(`Table ${table} check failed: ${error.message}`);
        }

        // 3. Check Recent Activity (Last 2 Hours)
        const twoHoursAgo = new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString();
        const { count, error: countError } = await supabase
            .from("system_logs")
            .select("*", { count: "exact", head: true })
            .gte("created_at", twoHoursAgo);

        if (countError) issues.push(`Activity check failed: ${countError.message}`);
        else if (count === 0) issues.push("No system activity in the last 2 hours.");

        // 4. Report & Alert
        const status = issues.length === 0 ? "healthy" : "unhealthy";

        // Log to DB
        await supabase.from("system_logs").insert({
            level: status === "healthy" ? "INFO" : "CRITICAL",
            message: `Heartbeat Check: ${status.toUpperCase()}`,
            metadata: { issues, timestamp: new Date().toISOString() }
        });

        // Send Email Alert if Unhealthy
        if (issues.length > 0 && resendApiKey) {
            console.log("Sending Alert...");
            await fetch("https://api.resend.com/emails", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${resendApiKey}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    from: "Empire Monitor <monitor@aiserviceco.com>",
                    to: [ALERT_EMAIL],
                    subject: `🚨 Empire Alert: ${issues.length} Issues Detected`,
                    html: `<h2>System Health Alert</h2><ul>${issues.map(i => `<li>${i}</li>`).join("")}</ul>`
                })
            });
        }

        return new Response(
            JSON.stringify({ status, issues }),
            { headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );

    } catch (error) {
        return new Response(
            JSON.stringify({ error: error.message }),
            { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
    }
});
