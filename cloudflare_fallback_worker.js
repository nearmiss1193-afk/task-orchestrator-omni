// Cloudflare Worker: Webhook Fallback Agent
// Exposes a POST endpoint that forwards inbound webhook payloads to the primary orchestrator.
// If the primary is unhealthy, forwards to a secondary fallback runner.
// Logs receipt and response status to Supabase.

export default {
    async fetch(request, env, ctx) {
        if (request.method !== "POST") {
            return new Response("Method not allowed", { status: 405 });
        }
        const payload = await request.clone().json();
        const primaryUrl = env.PRIMARY_URL; // e.g., https://nearmiss1193-afk--sovereign-orchestrator-health.modal.run/webhook
        const fallbackUrl = env.FALLBACK_URL; // e.g., https://empire-fallback-runner.up.railway.app/webhook

        const headers = { "Content-Type": "application/json", ...Object.fromEntries(request.headers) };
        let response;
        try {
            response = await fetch(primaryUrl, {
                method: "POST",
                body: JSON.stringify(payload),
                headers,
            });
            if (!response.ok) throw new Error("Primary failed");
        } catch (e) {
            // Forward to fallback
            response = await fetch(fallbackUrl, {
                method: "POST",
                body: JSON.stringify(payload),
                headers,
            });
        }

        // Log to Supabase (non-blocking)
        try {
            const supabaseUrl = "https://rzcpfwkygdvoshtwxncs.supabase.co";
            const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6Y3Bmd2t5Z2R2b3NodHd4bmNzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjU5MDQyNCwiZXhwIjoyMDgyMTY2NDI0fQ.wiyr_YDDkgtTZfv6sv0FCAmlfGhug81xdX8D6jHpTYo";
            await fetch(`${supabaseUrl}/rest/v1/webhook_logs`, {
                method: "POST",
                headers: {
                    "apikey": supabaseKey,
                    "Authorization": `Bearer ${supabaseKey}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    received_at: new Date().toISOString(),
                    primary_url: primaryUrl,
                    fallback_url: fallbackUrl,
                    status: response.ok ? "ok" : "error",
                    response_status: response.status,
                }),
            });
        } catch (logErr) {
            // ignore logging errors
        }

        // Return 200 quickly
        return new Response("", { status: 200 });
    },
};
